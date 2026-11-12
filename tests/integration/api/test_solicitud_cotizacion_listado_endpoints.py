from unittest.mock import MagicMock

import pytest

from app.main import app
from app.aplicacion.solicitud_cotizacion.dto.contadores_solicitudes_cotizacion import (
    ContadoresSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import (
    SolicitudCotizacionResumen,
)
from app.aplicacion.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_service import (
    ConsultaSolicitudesCotizacionService,
)
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_resumen_solicitudes_cotizacion_activas import (
    ObtenerResumenSolicitudesCotizacionActivasUseCase,
)
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import (
    get_obtener_resumen_solicitudes_cotizacion_activas_use_case,
)
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock


def _usuario_con_permisos(*codigos: str) -> Usuario:
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


def _resumen(id_solicitud: int = 1) -> SolicitudCotizacionResumen:
    return SolicitudCotizacionResumen(
        id=id_solicitud,
        id_prospecto=10,
        nombre_riesgo='Condominio Las Torres',
        informacion_completa=False,
        ejecutivo_comercial='Ana Pérez',
        tipo='incendio',
        recotizacion=False,
        motivo_recotizacion=None,
        producto='Incendio Condominio',
        prioridad='alta',
        fecha='2026-11-10T10:00:00',
        tiene_cotizaciones=True,
        campos_faltantes=['direccion'],
        estudio_disponible=False,
    )


CONTADORES = ContadoresSolicitudesCotizacion(
    informacion_incompleta=1,
    listas_para_cotizar=2,
    cotizaciones_emitidas=3,
    estudios_emitidos=4,
)


@pytest.fixture
def consulta_service_mock():
    service = MagicMock(spec=ConsultaSolicitudesCotizacionService)
    service.listar.return_value = ([_resumen()], 23)
    service.contadores.return_value = CONTADORES
    return service


@pytest.fixture
def usuario_global():
    return _usuario_con_permisos('VER_SOLICITUDES_COTIZACION_GLOBAL')


@pytest.fixture
def usuario_propio():
    return _usuario_con_permisos('VER_SOLICITUDES_COTIZACION_PROPIAS')


@pytest.fixture
def usuario_sin_permisos():
    return _usuario_con_permisos('OBTENER_PROSPECTOS_TODOS')


def _client(usuario, consulta_service_mock):
    use_case = ObtenerResumenSolicitudesCotizacionActivasUseCase(
        consulta_service=consulta_service_mock,
    )

    app.dependency_overrides[get_current_user] = lambda: usuario
    app.dependency_overrides[get_obtener_resumen_solicitudes_cotizacion_activas_use_case] = (
        lambda: use_case
    )

    from starlette.testclient import TestClient
    client = TestClient(app)
    return client


@pytest.fixture
def client_global(usuario_global, consulta_service_mock):
    client = _client(usuario_global, consulta_service_mock)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_propio(usuario_propio, consulta_service_mock):
    client = _client(usuario_propio, consulta_service_mock)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_sin_permisos(usuario_sin_permisos, consulta_service_mock):
    client = _client(usuario_sin_permisos, consulta_service_mock)
    yield client
    app.dependency_overrides.clear()


@pytest.mark.integration
class TestListadoSolicitudesCotizacionEndpoints:

    def test_shape_de_respuesta_sin_params(self, client_global):
        response = client_global.get('/solicitudes-cotizacion/')

        assert response.status_code == 200
        body = response.json()

        assert set(body.keys()) == {
            'data', 'contadores', 'total', 'pagina', 'tamano_pagina', 'total_paginas',
        }
        assert set(body['contadores'].keys()) == {
            'informacion_incompleta', 'listas_para_cotizar',
            'cotizaciones_emitidas', 'estudios_emitidos',
        }
        assert body['contadores'] == {
            'informacion_incompleta': 1,
            'listas_para_cotizar': 2,
            'cotizaciones_emitidas': 3,
            'estudios_emitidos': 4,
        }
        assert body['total'] == 23
        assert body['pagina'] == 1
        assert body['tamano_pagina'] == 10
        assert body['total_paginas'] == 3

        assert len(body['data']) == 1
        assert body['data'][0]['nombre_riesgo'] == 'Condominio Las Torres'
        assert body['data'][0]['tiene_cotizaciones'] is True
        assert body['data'][0]['campos_faltantes'] == ['direccion']

    def test_filtros_y_paginacion_llegan_al_servicio(self, client_global, consulta_service_mock):
        response = client_global.get(
            '/solicitudes-cotizacion/',
            params={
                'texto_busqueda': 'torres',
                'estado': 'listas_para_cotizar',
                'prioridad': 'alta',
                'rut_usuario': '12345678-9',
                'pagina': 2,
                'tamano_pagina': 5,
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body['pagina'] == 2
        assert body['tamano_pagina'] == 5

        filtro = consulta_service_mock.listar.call_args.args[1]
        assert filtro.texto_busqueda == 'torres'
        assert filtro.estado == 'listas_para_cotizar'
        assert filtro.prioridad == 'alta'
        assert filtro.rut_usuario == '12345678-9'
        assert filtro.pagina == 2
        assert filtro.tamano_pagina == 5

    def test_estado_invalido_devuelve_400(self, client_global, consulta_service_mock):
        response = client_global.get(
            '/solicitudes-cotizacion/',
            params={'estado': 'con_cotizaciones'},
        )

        assert response.status_code == 400
        consulta_service_mock.listar.assert_not_called()

    def test_prioridad_invalida_devuelve_400(self, client_global, consulta_service_mock):
        response = client_global.get(
            '/solicitudes-cotizacion/',
            params={'prioridad': 'media'},
        )

        assert response.status_code == 400
        consulta_service_mock.listar.assert_not_called()

    def test_scoping_propias_filtra_por_rut_del_usuario(self, client_propio, consulta_service_mock):
        response = client_propio.get('/solicitudes-cotizacion/')

        assert response.status_code == 200
        assert consulta_service_mock.listar.call_args.args[0] == '12345678-9'
        consulta_service_mock.contadores.assert_called_once_with('12345678-9')

    def test_scoping_global_no_filtra(self, client_global, consulta_service_mock):
        response = client_global.get('/solicitudes-cotizacion/')

        assert response.status_code == 200
        assert consulta_service_mock.listar.call_args.args[0] is None
        consulta_service_mock.contadores.assert_called_once_with(None)

    def test_total_paginas_se_redondea_hacia_arriba(self, client_global, consulta_service_mock):
        response = client_global.get(
            '/solicitudes-cotizacion/',
            params={'tamano_pagina': 10},
        )

        assert response.json()['total_paginas'] == 3

        consulta_service_mock.listar.return_value = ([], 0)
        response = client_global.get(
            '/solicitudes-cotizacion/',
            params={'tamano_pagina': 10},
        )

        body = response.json()
        assert body['total'] == 0
        assert body['total_paginas'] == 1

    def test_sin_permisos_devuelve_403(self, client_sin_permisos):
        response = client_sin_permisos.get('/solicitudes-cotizacion/')

        assert response.status_code == 403
