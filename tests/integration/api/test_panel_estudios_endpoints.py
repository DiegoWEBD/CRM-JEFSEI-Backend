from unittest.mock import MagicMock

import pytest

from app.main import app
from app.aplicacion.solicitud_cotizacion.dto.contadores_panel_cotizaciones import (
    ContadoresPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.dto.cotizacion_resumen import CotizacionResumen
from app.aplicacion.solicitud_cotizacion.dto.fila_panel_cotizaciones import (
    FilaPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.servicios.consulta_panel_cotizaciones_service import (
    ConsultaPanelCotizacionesService,
)
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_panel_cotizaciones import (
    ObtenerPanelCotizacionesUseCase,
)
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import (
    get_obtener_panel_cotizaciones_use_case,
)
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock


def _usuario_con_permisos(*codigos: str) -> Usuario:
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


def _fila(id_solicitud: int = 1) -> FilaPanelCotizaciones:
    return FilaPanelCotizaciones(
        id=id_solicitud,
        id_prospecto=101,
        id_proceso_comercial=202,
        cliente='Condominio Las Torres',
        linea_seguro='Incendio Condominio',
        ejecutivo_comercial='Ana Pérez',
        prioridad='alta',
        fecha='2026-11-10T10:00:00',
        cantidad_cotizaciones=1,
        vencimiento_mas_proximo='2026-12-01T00:00:00',
        estado='VIGENTE',
        tiene_estudio=False,
        id_estudio=None,
        cotizaciones=[
            CotizacionResumen(
                id=11,
                company='Company',
                prima_neta=10.0,
                prima_bruta=11.9,
                fecha_vencimiento='2026-12-01T00:00:00',
                estado='VIGENTE',
            )
        ],
    )


CONTADORES = ContadoresPanelCotizaciones(
    cotizaciones_vigentes=1,
    cotizaciones_por_vencer=2,
    cotizaciones_vencidas=3,
    estudios_pendientes=4,
    estudios_emitidos=5,
)


@pytest.fixture
def consulta_service_mock():
    service = MagicMock(spec=ConsultaPanelCotizacionesService)
    service.listar.return_value = ([_fila()], 23)
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
    use_case = ObtenerPanelCotizacionesUseCase(
        consulta_service=consulta_service_mock,
    )

    app.dependency_overrides[get_current_user] = lambda: usuario
    app.dependency_overrides[get_obtener_panel_cotizaciones_use_case] = (
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
class TestPanelCotizacionesEstudiosEndpoints:

    def test_shape_de_respuesta_sin_params(self, client_global):
        response = client_global.get('/solicitudes-cotizacion/panel-estudios')

        assert response.status_code == 200
        body = response.json()

        assert set(body.keys()) == {
            'data', 'contadores', 'total', 'pagina', 'tamano_pagina', 'total_paginas',
        }
        assert set(body['contadores'].keys()) == {
            'cotizaciones_vigentes', 'cotizaciones_por_vencer',
            'cotizaciones_vencidas', 'estudios_pendientes', 'estudios_emitidos',
        }
        assert body['contadores'] == {
            'cotizaciones_vigentes': 1,
            'cotizaciones_por_vencer': 2,
            'cotizaciones_vencidas': 3,
            'estudios_pendientes': 4,
            'estudios_emitidos': 5,
        }
        assert body['total'] == 23
        assert body['pagina'] == 1
        assert body['tamano_pagina'] == 10
        assert body['total_paginas'] == 3

        assert len(body['data']) == 1
        fila = body['data'][0]
        assert fila['cliente'] == 'Condominio Las Torres'
        assert fila['linea_seguro'] == 'Incendio Condominio'
        assert fila['cantidad_cotizaciones'] == 1
        assert fila['estado'] == 'VIGENTE'
        assert len(fila['cotizaciones']) == 1
        assert fila['cotizaciones'][0]['company'] == 'Company'
        assert fila['cotizaciones'][0]['estado'] == 'VIGENTE'

    def test_filtros_y_paginacion_llegan_al_servicio(self, client_global, consulta_service_mock):
        response = client_global.get(
            '/solicitudes-cotizacion/panel-estudios',
            params={
                'texto_busqueda': 'torres',
                'estado': 'cotizaciones_vigentes',
                'prioridad': 'alta',
                'rut_ejecutivo': '12345678-9',
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
        assert filtro.estado == 'cotizaciones_vigentes'
        assert filtro.prioridad == 'alta'
        assert filtro.rut_ejecutivo == '12345678-9'
        assert filtro.pagina == 2
        assert filtro.tamano_pagina == 5

    def test_acepta_los_cinco_estados_del_panel(self, client_global, consulta_service_mock):
        for estado in (
            'cotizaciones_vigentes',
            'cotizaciones_por_vencer',
            'cotizaciones_vencidas',
            'estudios_pendientes',
            'estudios_emitidos',
        ):
            response = client_global.get(
                '/solicitudes-cotizacion/panel-estudios',
                params={'estado': estado},
            )

            assert response.status_code == 200
            assert consulta_service_mock.listar.call_args.args[1].estado == estado

    def test_estado_invalido_devuelve_400(self, client_global, consulta_service_mock):
        response = client_global.get(
            '/solicitudes-cotizacion/panel-estudios',
            params={'estado': 'con_cotizaciones'},
        )

        assert response.status_code == 400
        consulta_service_mock.listar.assert_not_called()

    def test_prioridad_invalida_devuelve_400(self, client_global, consulta_service_mock):
        response = client_global.get(
            '/solicitudes-cotizacion/panel-estudios',
            params={'prioridad': 'media'},
        )

        assert response.status_code == 400
        consulta_service_mock.listar.assert_not_called()

    def test_scoping_propias_filtra_por_rut_del_usuario(self, client_propio, consulta_service_mock):
        response = client_propio.get('/solicitudes-cotizacion/panel-estudios')

        assert response.status_code == 200
        assert consulta_service_mock.listar.call_args.args[0] == '12345678-9'
        consulta_service_mock.contadores.assert_called_once_with('12345678-9')

    def test_scoping_global_no_filtra(self, client_global, consulta_service_mock):
        response = client_global.get('/solicitudes-cotizacion/panel-estudios')

        assert response.status_code == 200
        assert consulta_service_mock.listar.call_args.args[0] is None
        consulta_service_mock.contadores.assert_called_once_with(None)

    def test_total_paginas_se_redondea_hacia_arriba(self, client_global, consulta_service_mock):
        response = client_global.get(
            '/solicitudes-cotizacion/panel-estudios',
            params={'tamano_pagina': 10},
        )

        assert response.json()['total_paginas'] == 3

        consulta_service_mock.listar.return_value = ([], 0)
        response = client_global.get(
            '/solicitudes-cotizacion/panel-estudios',
            params={'tamano_pagina': 10},
        )

        body = response.json()
        assert body['total'] == 0
        assert body['total_paginas'] == 1

    def test_sin_permisos_devuelve_403(self, client_sin_permisos):
        response = client_sin_permisos.get('/solicitudes-cotizacion/panel-estudios')

        assert response.status_code == 403
