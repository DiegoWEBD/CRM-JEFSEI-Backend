from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.usuario_factory import crear_usuario_mock

PERMISO_REG_TODOS = 'REGISTRAR_GESTION_COMERCIAL_TODOS'
PERMISO_REG_PROPIOS = 'REGISTRAR_GESTION_COMERCIAL_PROPIOS'
PERMISO_VER_TODOS = 'VER_GESTIONES_COMERCIALES_TODOS'
PERMISO_VER_PROPIOS = 'VER_GESTIONES_COMERCIALES_PROPIOS'


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='11111111-1')


@pytest.fixture
def repositorio_usuarios_mock():
    mock = MagicMock(spec=RepositorioUsuarios)
    mock.usuario_tiene_permiso.return_value = False
    return mock


@pytest.fixture
def authorization_repository_mock():
    return MagicMock(spec=AuthorizationRepository)


@pytest.fixture
def authorization_service(repositorio_usuarios_mock, authorization_repository_mock):
    return AuthorizationService(
        authorization_repository=authorization_repository_mock,
        repositorio_prospectos=MagicMock(spec=RepositorioProspectos),
        repositorio_usuarios=repositorio_usuarios_mock,
        repositorio_procesos_comerciales=MagicMock(spec=RepositorioProcesosComerciales),
        repositorio_solicitudes_cotizacion=MagicMock(spec=RepositorioSolicitudesCotizacion),
    )


def _con_permiso(repositorio_usuarios_mock, *codigos):
    repositorio_usuarios_mock.usuario_tiene_permiso.side_effect = (
        lambda usuario, codigo: codigo in codigos
    )


@pytest.mark.unit
class TestUsuarioPuedeRegistrarGestionComercial:

    def test_permiso_todos_permite_cualquier_prospecto(
        self, authorization_service, repositorio_usuarios_mock, authorization_repository_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_REG_TODOS)

        assert authorization_service.usuario_puede_registrar_gestion_comercial(usuario, 7) is True
        authorization_repository_mock.usuario_asignado_a_prospecto.assert_not_called()

    def test_permiso_propios_con_asignacion_permite(
        self, authorization_service, repositorio_usuarios_mock, authorization_repository_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_REG_PROPIOS)
        authorization_repository_mock.usuario_asignado_a_prospecto.return_value = True

        assert authorization_service.usuario_puede_registrar_gestion_comercial(usuario, 7) is True
        authorization_repository_mock.usuario_asignado_a_prospecto.assert_called_once_with('11111111-1', 7)

    def test_permiso_propios_sin_asignacion_deniega(
        self, authorization_service, repositorio_usuarios_mock, authorization_repository_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_REG_PROPIOS)
        authorization_repository_mock.usuario_asignado_a_prospecto.return_value = False

        assert authorization_service.usuario_puede_registrar_gestion_comercial(usuario, 7) is False

    def test_sin_permisos_deniega(
        self, authorization_service, repositorio_usuarios_mock, authorization_repository_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock)

        assert authorization_service.usuario_puede_registrar_gestion_comercial(usuario, 7) is False
        authorization_repository_mock.usuario_asignado_a_prospecto.assert_not_called()

    def test_obtener_prospectos_todos_no_interviene(
        self, authorization_service, repositorio_usuarios_mock, authorization_repository_mock, usuario
    ):
        # OBTENER_PROSPECTOS_TODOS no es bypass del registro de gestiones.
        _con_permiso(repositorio_usuarios_mock, PERMISO_REG_PROPIOS, 'OBTENER_PROSPECTOS_TODOS')
        authorization_repository_mock.usuario_asignado_a_prospecto.return_value = False

        assert authorization_service.usuario_puede_registrar_gestion_comercial(usuario, 7) is False


@pytest.mark.unit
class TestUsuarioPuedeVerGestionesComercialesProspecto:

    def test_permiso_todos_permite_cualquier_prospecto(
        self, authorization_service, repositorio_usuarios_mock, authorization_repository_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_VER_TODOS)

        assert authorization_service.usuario_puede_ver_gestiones_comerciales_prospecto(usuario, 7) is True
        authorization_repository_mock.usuario_asignado_a_prospecto.assert_not_called()

    def test_permiso_propios_con_asignacion_permite(
        self, authorization_service, repositorio_usuarios_mock, authorization_repository_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_VER_PROPIOS)
        authorization_repository_mock.usuario_asignado_a_prospecto.return_value = True

        assert authorization_service.usuario_puede_ver_gestiones_comerciales_prospecto(usuario, 7) is True

    def test_permiso_propios_sin_asignacion_deniega(
        self, authorization_service, repositorio_usuarios_mock, authorization_repository_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_VER_PROPIOS)
        authorization_repository_mock.usuario_asignado_a_prospecto.return_value = False

        assert authorization_service.usuario_puede_ver_gestiones_comerciales_prospecto(usuario, 7) is False

    def test_sin_permisos_deniega(
        self, authorization_service, repositorio_usuarios_mock, authorization_repository_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock)

        assert authorization_service.usuario_puede_ver_gestiones_comerciales_prospecto(usuario, 7) is False


@pytest.mark.unit
class TestUsuarioPuedeVerTodasLasGestionesComerciales:

    def test_permiso_todos_es_global(self, authorization_service, repositorio_usuarios_mock, usuario):
        _con_permiso(repositorio_usuarios_mock, PERMISO_VER_TODOS)

        assert authorization_service.usuario_puede_ver_todas_las_gestiones_comerciales(usuario) is True

    def test_solo_propios_no_es_global(self, authorization_service, repositorio_usuarios_mock, usuario):
        _con_permiso(repositorio_usuarios_mock, PERMISO_VER_PROPIOS)

        assert authorization_service.usuario_puede_ver_todas_las_gestiones_comerciales(usuario) is False
