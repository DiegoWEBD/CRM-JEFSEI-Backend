import pytest
from unittest.mock import MagicMock

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.recordatorio.use_cases.obtener_proximo_contacto import ObtenerProximoContactoUseCase
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from tests.factories.recordatorio_factory import crear_recordatorio_usuario_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_recordatorios_mock():
    return MagicMock(spec=RepositorioRecordatorios)


@pytest.fixture
def authorization_service_mock():
    return MagicMock(spec=AuthorizationService)


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='11111111-1')


@pytest.fixture
def use_case(repositorio_recordatorios_mock, authorization_service_mock):
    return ObtenerProximoContactoUseCase(repositorio_recordatorios_mock, authorization_service_mock)


@pytest.mark.unit
class TestObtenerProximoContactoUseCase:

    def test_consulta_propio_sin_rechequeo(self, use_case, repositorio_recordatorios_mock, authorization_service_mock, usuario):
        recordatorio = crear_recordatorio_usuario_mock()
        repositorio_recordatorios_mock.obtener_proximo_contacto.return_value = recordatorio

        resultado = use_case.ejecutar(usuario=usuario, rut_objetivo='11111111-1', id_prospecto=7)

        assert resultado == recordatorio
        repositorio_recordatorios_mock.obtener_proximo_contacto.assert_called_once_with('11111111-1', 7)
        authorization_service_mock.usuario_puede_gestionar_recordatorio_ajeno.assert_not_called()

    def test_consulta_ajeno_con_permiso_global(self, use_case, repositorio_recordatorios_mock, authorization_service_mock, usuario):
        recordatorio = crear_recordatorio_usuario_mock()
        repositorio_recordatorios_mock.obtener_proximo_contacto.return_value = recordatorio
        authorization_service_mock.usuario_puede_gestionar_recordatorio_ajeno.return_value = True

        resultado = use_case.ejecutar(usuario=usuario, rut_objetivo='22222222-2', id_prospecto=7)

        assert resultado == recordatorio
        authorization_service_mock.usuario_puede_gestionar_recordatorio_ajeno.assert_called_once_with(usuario)
        repositorio_recordatorios_mock.obtener_proximo_contacto.assert_called_once_with('22222222-2', 7)

    def test_consulta_ajeno_sin_permiso_global_retorna_403(self, use_case, repositorio_recordatorios_mock, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_gestionar_recordatorio_ajeno.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario, rut_objetivo='22222222-2', id_prospecto=7)

        repositorio_recordatorios_mock.obtener_proximo_contacto.assert_not_called()
