from unittest.mock import MagicMock

import pytest

from app.aplicacion.cotizacion.use_cases.registrar_cotizacion_a_solicitud import (
    RegistrarCotizacionASolicitudUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.cotizacion.dependencias.deps import (
    get_registrar_cotizacion_a_solicitud_use_case,
)
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock


def _usuario_con_permisos(*codigos: str) -> Usuario:
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


FORM_COTIZACION = {
    'tipo': 'prima',
    'monto_total_asegurado': '1000',
    'asistencia_afecta': '0',
    'asistencia_excenta': '0',
    'id_company': '1',
    'fecha_emision': '2026-01-01T00:00:00',
    'fecha_vencimiento': '2027-01-01T00:00:00',
    'prima_afecta': '100',
    'prima_excenta': '50',
}

URL = '/solicitudes-cotizacion/3/cotizaciones'


@pytest.fixture
def use_case_mock():
    return MagicMock(spec=RegistrarCotizacionASolicitudUseCase)


@pytest.fixture
def usuario_con_carga():
    return _usuario_con_permisos('CARGAR_COTIZACIONES')


@pytest.fixture
def usuario_sin_permisos():
    # Puede ver solicitudes, pero no cargar cotizaciones: el endpoint es de
    # escritura y exige CARGAR_COTIZACIONES (re-chequeo de ownership aparte).
    return _usuario_con_permisos('VER_SOLICITUDES_COTIZACION_PROPIAS')


def _client(usuario, use_case_mock):
    def override_get_current_user():
        return usuario

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_registrar_cotizacion_a_solicitud_use_case] = lambda: use_case_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_con_permiso(usuario_con_carga, use_case_mock):
    yield from _client(usuario_con_carga, use_case_mock)


@pytest.fixture
def client_sin_permiso(usuario_sin_permisos, use_case_mock):
    yield from _client(usuario_sin_permisos, use_case_mock)


@pytest.mark.integration
class TestRegistrarCotizacionASolicitudEndpoint:

    def test_sin_permiso_de_carga_retorna_403(self, client_sin_permiso, use_case_mock, headers_auth_validos):
        response = client_sin_permiso.post(URL, data=FORM_COTIZACION, headers=headers_auth_validos)

        assert response.status_code == 403
        use_case_mock.ejecutar.assert_not_called()

    def test_sin_ownership_retorna_403(self, client_con_permiso, use_case_mock, headers_auth_validos):
        use_case_mock.ejecutar.side_effect = UsuarioNoAutorizadoException

        response = client_con_permiso.post(URL, data=FORM_COTIZACION, headers=headers_auth_validos)

        assert response.status_code == 403
        use_case_mock.ejecutar.assert_called_once()

    def test_solicitud_inexistente_retorna_404(self, client_con_permiso, use_case_mock, headers_auth_validos):
        use_case_mock.ejecutar.side_effect = RecursoNoEncontradoException('Solicitud no encontrada')

        response = client_con_permiso.post(URL, data=FORM_COTIZACION, headers=headers_auth_validos)

        assert response.status_code == 404

    def test_proceso_cerrado_retorna_409(self, client_con_permiso, use_case_mock, headers_auth_validos):
        use_case_mock.ejecutar.side_effect = ConflictoEnAccionException(
            'No se puede cargar una cotización de una oportunidad cerrada'
        )

        response = client_con_permiso.post(URL, data=FORM_COTIZACION, headers=headers_auth_validos)

        assert response.status_code == 409

    def test_registro_exitoso_retorna_201(self, client_con_permiso, use_case_mock, headers_auth_validos):
        use_case_mock.ejecutar.return_value = None

        response = client_con_permiso.post(URL, data=FORM_COTIZACION, headers=headers_auth_validos)

        assert response.status_code == 201
        use_case_mock.ejecutar.assert_called_once()
