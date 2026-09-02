import pytest
from unittest.mock import MagicMock
from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.aplicacion.auth.dtos.iniciar_sesion_response_dto import IniciarSesionResponseDTO
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.aplicacion.auth.authentication_service import AuthenticationService
from tests.factories.usuario_factory import crear_usuario_mock, crear_rol_mock, crear_permiso_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioUsuarios)


@pytest.fixture
def auth_service_mock():
    return MagicMock(spec=AuthenticationService)


@pytest.fixture
def use_case(repositorio_mock, auth_service_mock):
    return IniciarSesionUseCase(repositorio_mock, auth_service_mock)


@pytest.mark.unit
class TestIniciarSesionUseCase:

    def test_login_exitoso(self, use_case, repositorio_mock, auth_service_mock):
        permisos = [crear_permiso_mock(codigo="VER_USUARIOS")]
        rol = crear_rol_mock(permisos=permisos)
        usuario = crear_usuario_mock(roles=[rol], password_hash="hash_valido")

        repositorio_mock.buscar.return_value = usuario
        auth_service_mock.verificar_password.return_value = True
        auth_service_mock.crear_access_token.return_value = "token_123"

        resultado = use_case.execute(rut="12345678-9", password="password123")

        assert resultado is not None
        assert isinstance(resultado, IniciarSesionResponseDTO)
        assert resultado.access_token == "token_123"
        assert resultado.usuario.rut == "12345678-9"

    def test_login_usuario_no_encontrado(self, use_case, repositorio_mock):
        repositorio_mock.buscar.return_value = None

        resultado = use_case.execute(rut="99999999-9", password="password123")

        assert resultado is None

    def test_login_password_incorrecta(self, use_case, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(password_hash="hash_valido")
        repositorio_mock.buscar.return_value = usuario
        auth_service_mock.verificar_password.return_value = False

        resultado = use_case.execute(rut="12345678-9", password="wrong_password")

        assert resultado is None

    def test_login_usuario_deshabilitado(self, use_case, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(habilitado=False)
        repositorio_mock.buscar.return_value = usuario

        resultado = use_case.execute(rut="12345678-9", password="password123")

        assert resultado is None

    def test_login_usuario_eliminado(self, use_case, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(eliminado=True)
        repositorio_mock.buscar.return_value = usuario

        resultado = use_case.execute(rut="12345678-9", password="password123")

        assert resultado is None

    def test_login_sin_password_hash(self, use_case, repositorio_mock):
        usuario = crear_usuario_mock(password_hash=None)
        repositorio_mock.buscar.return_value = usuario

        resultado = use_case.execute(rut="12345678-9", password="password123")

        assert resultado is None

    def test_login_genera_token_con_permisos(self, use_case, repositorio_mock, auth_service_mock):
        permisos = [
            crear_permiso_mock(codigo="VER_USUARIOS"),
            crear_permiso_mock(codigo="CREAR_PROSPECTOS"),
        ]
        rol = crear_rol_mock(codigo="EJECUTIVO", permisos=permisos)
        usuario = crear_usuario_mock(roles=[rol], password_hash="hash_valido")

        repositorio_mock.buscar.return_value = usuario
        auth_service_mock.verificar_password.return_value = True
        auth_service_mock.crear_access_token.return_value = "token_123"

        use_case.execute(rut="12345678-9", password="password123")

        call_args = auth_service_mock.crear_access_token.call_args[0][0]
        assert "rut" in call_args
        assert "codigo_roles" in call_args
        assert "codigo_permisos" in call_args
        assert "VER_USUARIOS" in call_args["codigo_permisos"]
        assert "CREAR_PROSPECTOS" in call_args["codigo_permisos"]
