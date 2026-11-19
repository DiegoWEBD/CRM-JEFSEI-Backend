from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.usuario_factory import crear_usuario_mock

PERMISO_GLOBAL = 'GESTIONAR_RECORDATORIO_GLOBAL'
PERMISO_PROPIO = 'GESTIONAR_RECORDATORIO_PROPIO'


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='11111111-1')


@pytest.fixture
def repositorio_usuarios_mock():
    mock = MagicMock(spec=RepositorioUsuarios)
    mock.usuario_tiene_permiso.return_value = False
    return mock


@pytest.fixture
def repositorio_recordatorios_mock():
    return MagicMock(spec=RepositorioRecordatorios)


@pytest.fixture
def authorization_service(repositorio_usuarios_mock, repositorio_recordatorios_mock):
    return AuthorizationService(
        authorization_repository=MagicMock(spec=AuthorizationRepository),
        repositorio_prospectos=MagicMock(spec=RepositorioProspectos),
        repositorio_usuarios=repositorio_usuarios_mock,
        repositorio_procesos_comerciales=MagicMock(spec=RepositorioProcesosComerciales),
        repositorio_solicitudes_cotizacion=MagicMock(spec=RepositorioSolicitudesCotizacion),
        repositorio_recordatorios=repositorio_recordatorios_mock,
    )


def _con_permiso(repositorio_usuarios_mock, *codigos):
    repositorio_usuarios_mock.usuario_tiene_permiso.side_effect = (
        lambda usuario, codigo: codigo in codigos
    )


@pytest.mark.unit
class TestUsuarioPuedeGestionarRecordatorio:

    def test_permiso_global_permite_recordatorio_ajeno(
        self, authorization_service, repositorio_usuarios_mock, repositorio_recordatorios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_GLOBAL)
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['22222222-2']

        assert authorization_service.usuario_puede_gestionar_recordatorio(usuario, 1) is True
        repositorio_recordatorios_mock.buscar_propietarios.assert_not_called()

    def test_permiso_propio_permite_recordatorio_propio(
        self, authorization_service, repositorio_usuarios_mock, repositorio_recordatorios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_PROPIO)
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['11111111-1']

        assert authorization_service.usuario_puede_gestionar_recordatorio(usuario, 1) is True

    def test_permiso_propio_deniega_recordatorio_ajeno(
        self, authorization_service, repositorio_usuarios_mock, repositorio_recordatorios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_PROPIO)
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['22222222-2']

        assert authorization_service.usuario_puede_gestionar_recordatorio(usuario, 1) is False

    def test_permiso_propio_deniega_recordatorio_inexistente(
        self, authorization_service, repositorio_usuarios_mock, repositorio_recordatorios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_PROPIO)
        repositorio_recordatorios_mock.buscar_propietarios.return_value = None

        assert authorization_service.usuario_puede_gestionar_recordatorio(usuario, 1) is False

    def test_sin_permisos_deniega(
        self, authorization_service, repositorio_usuarios_mock, repositorio_recordatorios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock)

        assert authorization_service.usuario_puede_gestionar_recordatorio(usuario, 1) is False
        repositorio_recordatorios_mock.buscar_propietarios.assert_not_called()

    def test_propietario_en_cobranza_cuenta_como_propio(
        self, authorization_service, repositorio_usuarios_mock, repositorio_recordatorios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_PROPIO)
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['11111111-1', '33333333-3']

        assert authorization_service.usuario_puede_gestionar_recordatorio(usuario, 1) is True


@pytest.mark.unit
class TestUsuarioPuedeGestionarRecordatorioAjeno:

    def test_permiso_global_permite(self, authorization_service, repositorio_usuarios_mock, usuario):
        _con_permiso(repositorio_usuarios_mock, PERMISO_GLOBAL)

        assert authorization_service.usuario_puede_gestionar_recordatorio_ajeno(usuario) is True

    def test_solo_permiso_propio_deniega(self, authorization_service, repositorio_usuarios_mock, usuario):
        _con_permiso(repositorio_usuarios_mock, PERMISO_PROPIO)

        assert authorization_service.usuario_puede_gestionar_recordatorio_ajeno(usuario) is False

    def test_sin_permisos_deniega(self, authorization_service, repositorio_usuarios_mock, usuario):
        _con_permiso(repositorio_usuarios_mock)

        assert authorization_service.usuario_puede_gestionar_recordatorio_ajeno(usuario) is False
