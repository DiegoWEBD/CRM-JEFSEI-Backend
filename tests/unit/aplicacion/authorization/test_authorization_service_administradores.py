from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='11111111-1')


@pytest.fixture
def repositorio_usuarios_mock():
    mock = MagicMock(spec=RepositorioUsuarios)
    mock.usuario_tiene_permiso.return_value = False
    return mock


@pytest.fixture
def authorization_service(repositorio_usuarios_mock):
    return AuthorizationService(
        authorization_repository=MagicMock(spec=AuthorizationRepository),
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
class TestUsuarioPuedeVerAdministradores:

    def test_con_permiso_permite(self, authorization_service, repositorio_usuarios_mock, usuario):
        _con_permiso(repositorio_usuarios_mock, 'VER_ADMINISTRADORES')

        assert authorization_service.usuario_puede_ver_administradores(usuario) is True

    def test_sin_permiso_deniega(self, authorization_service, repositorio_usuarios_mock, usuario):
        _con_permiso(repositorio_usuarios_mock)

        assert authorization_service.usuario_puede_ver_administradores(usuario) is False


@pytest.mark.unit
class TestUsuarioPuedeAdministrarAdministradores:

    def test_con_permiso_permite(self, authorization_service, repositorio_usuarios_mock, usuario):
        _con_permiso(repositorio_usuarios_mock, 'ADMINISTRAR_ADMINISTRADORES')

        assert authorization_service.usuario_puede_administrar_administradores(usuario) is True

    def test_solo_ver_no_permite_administrar(self, authorization_service, repositorio_usuarios_mock, usuario):
        _con_permiso(repositorio_usuarios_mock, 'VER_ADMINISTRADORES')

        assert authorization_service.usuario_puede_administrar_administradores(usuario) is False
