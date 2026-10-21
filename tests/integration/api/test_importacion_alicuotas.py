import io
import json

import pytest
from openpyxl import Workbook
from unittest.mock import MagicMock

from app.aplicacion.proceso_comercial.use_cases.importar_alicuota_oportunidad import (
    ImportarAlicuotaOportunidadUseCase,
)
from app.aplicacion.proceso_comercial.use_cases.obtener_alicuota_oportunidad import (
    ObtenerAlicuotaOportunidadUseCase,
)
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.proceso_comercial.dependencias.deps import (
    get_importar_alicuota_oportunidad_use_case,
    get_obtener_alicuota_oportunidad_use_case,
)
from tests.factories.auth_factory import crear_token_mock, headers_auth
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock

CONTENT_TYPE_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def _xlsx(filas=None) -> bytes:
    """Genera un .xlsx sintético con la estructura habitual de alícuotas."""

    if filas is None:
        filas = [
            ['Departamento', 'Dirección', 'Alícuota'],
            ['Depto 1', 'A 101', 2.5],
            ['Depto 2', 'A 102', 1.5],
        ]

    wb = Workbook()
    hoja = wb.active
    hoja.title = 'Alícuotas'

    for fila in filas:
        hoja.append(fila)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def _usuario_con_permisos(*permisos: str):
    return crear_usuario_mock(
        roles=[crear_rol_mock(
            codigo='EJECUTIVO',
            nombre='Ejecutivo comercial',
            permisos=[crear_permiso_mock(codigo=codigo) for codigo in permisos],
        )],
    )


@pytest.fixture
def usuario_autenticado():
    return _usuario_con_permisos('SOLICITAR_COTIZACION', 'VER_SOLICITUDES_COTIZACION_PROPIAS')


@pytest.fixture
def token_valido():
    return crear_token_mock()


@pytest.fixture
def headers_auth_validos(token_valido):
    return headers_auth(token_valido)


@pytest.fixture
def client(usuario_autenticado):
    def override_get_current_user():
        return usuario_autenticado

    app.dependency_overrides[get_current_user] = override_get_current_user

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_sin_permiso():
    usuario = crear_usuario_mock(roles=[crear_rol_mock(permisos=[crear_permiso_mock(codigo='VER_ALERTAS')])])

    def override_get_current_user():
        return usuario

    app.dependency_overrides[get_current_user] = override_get_current_user

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_unidades(usuario_autenticado):
    def override_get_current_user():
        return usuario_autenticado

    def override_get_unidades():
        uc = MagicMock(spec=ObtenerAlicuotaOportunidadUseCase)
        uc.ejecutar.return_value = (
            'alicuota.xlsx',
            [
                UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=0.025, fila_origen=2),
                UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=0.015, fila_origen=3),
            ],
        )
        return uc

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_alicuota_oportunidad_use_case] = override_get_unidades

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_unidades_no_autorizado(usuario_autenticado):
    def override_get_current_user():
        return usuario_autenticado

    def override_get_unidades():
        uc = MagicMock(spec=ObtenerAlicuotaOportunidadUseCase)
        uc.ejecutar.side_effect = UsuarioNoAutorizadoException()
        return uc

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_alicuota_oportunidad_use_case] = override_get_unidades

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _archivo(nombre='alicuota.xlsx', contenido=None):
    return ('archivo', (nombre, contenido if contenido is not None else _xlsx(), CONTENT_TYPE_XLSX))


def _configuracion(**cambios):
    datos = {
        'hoja': 'Alícuotas',
        'fila_encabezados': 1,
        'columna_identificador': 1,
        'columna_prorrateo': 3,
        'primera_fila': 2,
        'ultima_fila': 3,
        'interpretacion_prorrateo': 'valor_porcentual',
    }
    datos.update(cambios)
    return json.dumps(datos)


@pytest.mark.integration
class TestAnalizarAlicuotasEndpoint:

    def test_analiza_archivo_valido(self, client, headers_auth_validos):
        response = client.post('/importacion-alicuotas/analizar', files=[_archivo()], headers=headers_auth_validos)

        assert response.status_code == 200
        body = response.json()
        assert body['hoja_seleccionada'] == 'Alícuotas'
        assert body['sugerencias']['fila_encabezados'] == 1
        assert body['sugerencias']['columna_identificador'] == 1
        assert body['sugerencias']['columna_prorrateo'] == 3

    def test_extension_no_permitida_es_rechazada(self, client, headers_auth_validos):
        response = client.post(
            '/importacion-alicuotas/analizar',
            files=[_archivo(nombre='alicuota.csv')],
            headers=headers_auth_validos,
        )

        assert response.status_code == 400

    def test_archivo_vacio_es_rechazado(self, client, headers_auth_validos):
        response = client.post(
            '/importacion-alicuotas/analizar',
            files=[_archivo(contenido=b'')],
            headers=headers_auth_validos,
        )

        assert response.status_code == 400

    def test_archivo_corrupto_es_rechazado(self, client, headers_auth_validos):
        response = client.post(
            '/importacion-alicuotas/analizar',
            files=[_archivo(contenido=b'contenido que no es un xlsx')],
            headers=headers_auth_validos,
        )

        assert response.status_code == 400

    def test_sin_permiso_es_rechazado(self, client_sin_permiso, headers_auth_validos):
        response = client_sin_permiso.post(
            '/importacion-alicuotas/analizar',
            files=[_archivo()],
            headers=headers_auth_validos,
        )

        assert response.status_code == 403


@pytest.mark.integration
class TestValidarAlicuotasEndpoint:

    def test_valida_configuracion_correcta(self, client, headers_auth_validos):
        response = client.post(
            '/importacion-alicuotas/validar',
            files=[_archivo()],
            data={'configuracion': _configuracion()},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        body = response.json()
        assert body['cantidad_registros'] == 2
        assert body['tiene_errores_bloqueantes'] is False
        assert body['suma_prorrateos'] == 0.04

    def test_configuracion_invalida_es_rechazada(self, client, headers_auth_validos):
        response = client.post(
            '/importacion-alicuotas/validar',
            files=[_archivo()],
            data={'configuracion': _configuracion(primera_fila=3, ultima_fila=2)},
            headers=headers_auth_validos,
        )

        assert response.status_code == 400

    def test_configuracion_mal_formada_es_rechazada(self, client, headers_auth_validos):
        response = client.post(
            '/importacion-alicuotas/validar',
            files=[_archivo()],
            data={'configuracion': 'no es json'},
            headers=headers_auth_validos,
        )

        assert response.status_code == 400

    def test_reporta_errores_bloqueantes_por_fila(self, client, headers_auth_validos):
        contenido = _xlsx(filas=[
            ['Departamento', 'Dirección', 'Alícuota'],
            ['Depto 1', 'A 101', None],
            ['Depto 2', 'A 102', 1.5],
        ])

        response = client.post(
            '/importacion-alicuotas/validar',
            files=[_archivo(contenido=contenido)],
            data={'configuracion': _configuracion()},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        body = response.json()
        assert body['tiene_errores_bloqueantes'] is True
        assert body['problemas'][0]['fila_origen'] == 2

    def test_archivo_corrupto_es_rechazado(self, client, headers_auth_validos):
        response = client.post(
            '/importacion-alicuotas/validar',
            files=[_archivo(contenido=b'corrupto')],
            data={'configuracion': _configuracion()},
            headers=headers_auth_validos,
        )

        assert response.status_code == 400


@pytest.mark.integration
class TestObtenerAlicuotaOportunidadEndpoint:

    def test_devuelve_las_unidades_importadas(self, client_unidades, headers_auth_validos):
        response = client_unidades.get('/procesos-comerciales/42/alicuota', headers=headers_auth_validos)

        assert response.status_code == 200
        body = response.json()
        assert body['nombre_excel'] == 'alicuota.xlsx'
        assert body['cantidad'] == 2
        assert body['unidades'][0]['identificador_unidad'] == 'Depto 1'

    def test_acceso_no_autorizado(self, client_unidades_no_autorizado, headers_auth_validos):
        response = client_unidades_no_autorizado.get(
            '/procesos-comerciales/42/alicuota', headers=headers_auth_validos
        )

        assert response.status_code == 403


@pytest.fixture
def client_importar(usuario_autenticado):
    def override_get_current_user():
        return usuario_autenticado

    uc = MagicMock(spec=ImportarAlicuotaOportunidadUseCase)

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_importar_alicuota_oportunidad_use_case] = lambda: uc

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c, uc

    app.dependency_overrides.clear()


@pytest.fixture
def client_importar_sin_permiso():
    usuario = crear_usuario_mock(roles=[crear_rol_mock(permisos=[crear_permiso_mock(codigo='VER_ALERTAS')])])

    def override_get_current_user():
        return usuario

    uc = MagicMock(spec=ImportarAlicuotaOportunidadUseCase)

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_importar_alicuota_oportunidad_use_case] = lambda: uc

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c, uc

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestImportarAlicuotaOportunidadEndpoint:

    def test_importa_la_alicuota_en_la_oportunidad(self, client_importar, headers_auth_validos):
        client, uc = client_importar

        response = client.post(
            '/procesos-comerciales/42/alicuota',
            headers=headers_auth_validos,
            json={
                'nombre_excel': 'alicuota.xlsx',
                'unidades': [
                    {'identificador_unidad': 'Depto 1', 'prorrateo': 0.025, 'fila_origen': 2},
                    {'identificador_unidad': 'Depto 2', 'prorrateo': 0.015, 'fila_origen': 3},
                ],
            },
        )

        assert response.status_code == 200
        assert response.json()['cantidad'] == 2

        kwargs = uc.ejecutar.call_args.kwargs
        assert kwargs['id_proceso_comercial'] == 42
        assert kwargs['nombre_excel'] == 'alicuota.xlsx'
        assert [u.identificador_unidad for u in kwargs['unidades']] == ['Depto 1', 'Depto 2']
        assert kwargs['unidades'][0].prorrateo == 0.025

    def test_sin_permiso_es_rechazado(self, client_importar_sin_permiso, headers_auth_validos):
        client, uc = client_importar_sin_permiso

        response = client.post(
            '/procesos-comerciales/42/alicuota',
            headers=headers_auth_validos,
            json={'nombre_excel': 'alicuota.xlsx', 'unidades': []},
        )

        assert response.status_code == 403
        uc.ejecutar.assert_not_called()
