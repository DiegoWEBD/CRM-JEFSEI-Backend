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
        auth_service_mock.crear_access_token_de_sesion.return_value = "token_123"
        auth_service_mock.crear_refresh_token.return_value = "refresh_123"

        resultado = use_case.execute(rut="12345678-9", password="password123")

        assert resultado is not None
        assert isinstance(resultado, IniciarSesionResponseDTO)
        assert resultado.access_token == "token_123"
        assert resultado.refresh_token == "refresh_123"
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
        auth_service_mock.crear_access_token_de_sesion.return_value = "token_123"
        auth_service_mock.crear_refresh_token.return_value = "refresh_123"

        use_case.execute(rut="12345678-9", password="password123")

        # El token se emite ligado a la sesión: el id viaja como jti.
        argumentos = auth_service_mock.crear_access_token_de_sesion.call_args
        call_args = argumentos[0][0]
        id_sesion = argumentos[0][1]
        assert "rut" in call_args
        assert "codigo_roles" in call_args
        assert "codigo_permisos" in call_args
        assert "VER_USUARIOS" in call_args["codigo_permisos"]
        assert "CREAR_PROSPECTOS" in call_args["codigo_permisos"]
        assert id_sesion

    def test_login_persiste_sesion_y_refresh_hasheado(
        self, repositorio_mock, auth_service_mock
    ):
        from unittest.mock import MagicMock as _MagicMock
        from app.dominio.auditoria.repositorio_sesiones import RepositorioSesiones

        usuario = crear_usuario_mock(password_hash="hash_valido")
        repositorio_mock.buscar.return_value = usuario
        auth_service_mock.verificar_password.return_value = True
        auth_service_mock.crear_access_token_de_sesion.return_value = "token_123"
        auth_service_mock.crear_refresh_token.return_value = "refresh_123"
        auth_service_mock.hashear_refresh_token.return_value = "hash_de_refresh_123"

        repo_sesiones = _MagicMock(spec=RepositorioSesiones)
        use_case = IniciarSesionUseCase(
            repositorio_mock, auth_service_mock, repositorio_sesiones=repo_sesiones
        )

        resultado = use_case.execute(rut="12345678-9", password="password123")

        repo_sesiones.crear.assert_called_once()
        repo_sesiones.crear_refresh_token.assert_called_once()
        # Nunca se guarda el refresh token en claro.
        assert repo_sesiones.crear_refresh_token.call_args[0][1] == "hash_de_refresh_123"
        assert resultado.id_sesion
