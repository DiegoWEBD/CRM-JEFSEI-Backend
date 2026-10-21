from unittest.mock import MagicMock

import pytest

from app.aplicacion.proceso_comercial.use_cases.generar_excel_desglose_reconstruccion_unidades import (
    GenerarExcelDesgloseReconstruccionUnidadesUseCase,
)
from app.aplicacion.proceso_comercial.use_cases.obtener_desglose_reconstruccion_unidades import (
    ObtenerDesgloseReconstruccionUnidadesUseCase,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.calculadora_desglose_reconstruccion import CalculadoraDesgloseReconstruccion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota
from app.infraestructura.solicitud_cotizacion.generador_excel_desglose_reconstruccion import (
    GeneradorExcelDesgloseReconstruccion,
)
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.proceso_comercial.dependencias.deps import (
    get_generar_excel_desglose_reconstruccion_unidades_use_case,
    get_obtener_desglose_reconstruccion_unidades_use_case,
)
from tests.factories.auth_factory import crear_token_mock, headers_auth
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock

CONTENT_TYPE_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def _usuario_con_permisos(*permisos: str):
    return crear_usuario_mock(
        roles=[crear_rol_mock(
            codigo='EJECUTIVO',
            nombre='Ejecutivo comercial',
            permisos=[crear_permiso_mock(codigo=codigo) for codigo in permisos],
        )],
    )


def _unidades_con_desglose():
    # 4.760 UF de reconstrucción: Depto 1 → 144,97 → 200 | Depto 2 → 331,03 → 400
    return CalculadoraDesgloseReconstruccion.calcular(4760.0, [
        UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=0.030456521, fila_origen=2),
        UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=0.069543479, fila_origen=3),
    ])


def _ruta_xlsx(tmp_path) -> str:
    generador = GeneradorExcelDesgloseReconstruccion(carpeta_base=str(tmp_path))
    return generador.generar(42, _unidades_con_desglose())


@pytest.fixture
def token_valido():
    return crear_token_mock()


@pytest.fixture
def headers_auth_validos(token_valido):
    return headers_auth(token_valido)


@pytest.fixture
def client_desglose(tmp_path):
    usuario = _usuario_con_permisos('VER_SOLICITUDES_COTIZACION_PROPIAS')

    def override_get_current_user():
        return usuario

    def override_get_obtener():
        uc = MagicMock(spec=ObtenerDesgloseReconstruccionUnidadesUseCase)
        uc.ejecutar.return_value = (600.0, _unidades_con_desglose())
        return uc

    def override_get_excel():
        uc = MagicMock(spec=GenerarExcelDesgloseReconstruccionUnidadesUseCase)
        uc.ejecutar.return_value = _ruta_xlsx(tmp_path)
        return uc

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_desglose_reconstruccion_unidades_use_case] = override_get_obtener
    app.dependency_overrides[get_generar_excel_desglose_reconstruccion_unidades_use_case] = override_get_excel

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_desglose_sin_permiso():
    usuario = _usuario_con_permisos('VER_ALERTAS')

    def override_get_current_user():
        return usuario

    app.dependency_overrides[get_current_user] = override_get_current_user

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestDesgloseReconstruccionUnidadesEndpoint:

    def test_devuelve_el_desglose_persistido(self, client_desglose, headers_auth_validos):
        response = client_desglose.get(
            '/procesos-comerciales/42/desglose-reconstruccion', headers=headers_auth_validos
        )

        assert response.status_code == 200
        body = response.json()
        assert body['desglose_calculado'] is True
        assert body['monto_asegurado_sugerido_unidades'] == 600.0
        assert body['cantidad'] == 2

        unidad = body['unidades'][0]
        assert unidad['identificador_unidad'] == 'Depto 1'
        assert unidad['prorrateo'] == 0.030456521
        assert unidad['monto_reconstruccion'] == 144.97
        assert unidad['monto_asegurado_sugerido'] == 200.0
        assert unidad['prorrateo_pago'] == pytest.approx(200.0 / 600.0)

    def test_descarga_el_excel(self, client_desglose, headers_auth_validos):
        response = client_desglose.get(
            '/procesos-comerciales/42/desglose-reconstruccion/excel', headers=headers_auth_validos
        )

        assert response.status_code == 200
        assert response.headers['content-type'] == CONTENT_TYPE_XLSX
        assert 'desglose_reconstruccion_oportunidad_42.xlsx' in response.headers['content-disposition']
        assert response.content[:2] == b'PK'  # el .xlsx es un ZIP

    def test_sin_permiso_es_rechazado(self, client_desglose_sin_permiso, headers_auth_validos):
        response = client_desglose_sin_permiso.get(
            '/procesos-comerciales/42/desglose-reconstruccion', headers=headers_auth_validos
        )

        assert response.status_code == 403

    def test_excel_sin_permiso_es_rechazado(self, client_desglose_sin_permiso, headers_auth_validos):
        response = client_desglose_sin_permiso.get(
            '/procesos-comerciales/42/desglose-reconstruccion/excel', headers=headers_auth_validos
        )

        assert response.status_code == 403
