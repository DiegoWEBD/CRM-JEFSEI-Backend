import pytest
from unittest.mock import MagicMock

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.gestion_comercial.use_cases.obtener_ultima_gestion_comercial import ObtenerUltimaGestionComercialUseCase
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales
from tests.factories.gestion_comercial_factory import crear_gestion_comercial_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_mock():
    mock = MagicMock(spec=RepositorioGestionesComerciales)
    mock.obtener_ultima.return_value = crear_gestion_comercial_mock()
    return mock


@pytest.fixture
def authorization_service_mock():
    return MagicMock(spec=AuthorizationService)


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='11111111-1')


@pytest.fixture
def use_case(repositorio_mock, authorization_service_mock):
    return ObtenerUltimaGestionComercialUseCase(repositorio_mock, authorization_service_mock)


@pytest.mark.unit
class TestObtenerUltimaGestionComercialUseCase:

    def test_con_autorizacion_retorna_gestion(
        self, use_case, repositorio_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_ver_gestiones_comerciales_prospecto.return_value = True

        resultado = use_case.ejecutar(usuario=usuario, id_prospecto=7)

        assert resultado is not None
        repositorio_mock.obtener_ultima.assert_called_once_with(id_prospecto=7)

    def test_prospecto_ajeno_retorna_403(
        self, use_case, repositorio_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_ver_gestiones_comerciales_prospecto.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario, id_prospecto=7)

        repositorio_mock.obtener_ultima.assert_not_called()
