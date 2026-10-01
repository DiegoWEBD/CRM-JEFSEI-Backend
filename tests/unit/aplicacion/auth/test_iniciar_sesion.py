from unittest.mock import MagicMock

import pytest

from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.aplicacion.auth.dtos.iniciar_sesion_response_dto import IniciarSesionResponseDTO
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from tests.factories.auditoria_factory import crear_contexto_peticion_mock
from tests.factories.usuario_factory import crear_usuario_mock, crear_rol_mock, crear_permiso_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioUsuarios)


@pytest.fixture
def auth_service_mock():
    return MagicMock(spec=AuthenticationService)


@pytest.fixture
def servicio_auditoria_mock():
    return MagicMock(spec=ServicioAuditoria)


@pytest.fixture
def contexto():
    return crear_contexto_peticion_mock()


@pytest.fixture
def use_case(repositorio_mock, auth_service_mock, servicio_auditoria_mock):
    return IniciarSesionUseCase(repositorio_mock, auth_service_mock, servicio_auditoria_mock)


@pytest.mark.unit
class TestIniciarSesionUseCase:

    def test_login_exitoso(self, use_case, repositorio_mock, auth_service_mock):
        permisos = [crear_permiso_mock(codigo="VER_USUARIOS")]
        rol = crear_rol_mock(permisos=permisos)
        usuario = crear_usuario_mock(roles=[rol], password_hash="hash_valido")

        repositorio_mock.buscar.return_value = usuario
        auth_service_mock.verificar_password.return_value = True
        auth_service_mock.crear_access_token.return_value = "token_123"

        resultado = use_case.execute(rut="12345678-9", password="password123", contexto=crear_contexto_peticion_mock())

        assert resultado is not None
        assert isinstance(resultado, IniciarSesionResponseDTO)
        assert resultado.access_token == "token_123"
        assert resultado.usuario.rut == "12345678-9"

    def test_login_exitoso_registra_evento_auditoria(
        self, use_case, repositorio_mock, auth_service_mock, servicio_auditoria_mock, contexto
    ):
        usuario = crear_usuario_mock(password_hash="hash_valido")
        repositorio_mock.buscar.return_value = usuario
        auth_service_mock.verificar_password.return_value = True

        use_case.execute(rut="12345678-9", password="password123", contexto=contexto)

        servicio_auditoria_mock.registrar_autenticacion.assert_called_once()
        kwargs = servicio_auditoria_mock.registrar_autenticacion.call_args.kwargs
        assert kwargs["evento"] == EventoAuditoria.LOGIN_EXITOSO
        assert kwargs["resultado"] == ResultadoAuditoria.EXITO
        assert kwargs["rut_usuario"] == "12345678-9"
        assert kwargs["nombre_usuario"] == usuario.nombre
        assert kwargs["contexto"] == contexto

    def test_login_usuario_no_encontrado(self, use_case, repositorio_mock):
        repositorio_mock.buscar.return_value = None

        resultado = use_case.execute(rut="99999999-9", password="password123", contexto=crear_contexto_peticion_mock())

        assert resultado is None

    def test_login_fallido_registra_evento_con_rut_intentado(
        self, use_case, repositorio_mock, servicio_auditoria_mock, contexto
    ):
        repositorio_mock.buscar.return_value = None

        resultado = use_case.execute(rut="99999999-9", password="password123", contexto=contexto)

        assert resultado is None
        servicio_auditoria_mock.registrar_autenticacion.assert_called_once()
        kwargs = servicio_auditoria_mock.registrar_autenticacion.call_args.kwargs
        assert kwargs["evento"] == EventoAuditoria.LOGIN_FALLIDO
        assert kwargs["resultado"] == ResultadoAuditoria.FALLIDO
        assert kwargs["rut_usuario"] == "99999999-9"
        assert kwargs["contexto"] == contexto

    def test_login_fallido_nunca_registra_la_password(
        self, use_case, repositorio_mock, auth_service_mock, servicio_auditoria_mock, contexto
    ):
        usuario = crear_usuario_mock(password_hash="hash_valido")
        repositorio_mock.buscar.return_value = usuario
        auth_service_mock.verificar_password.return_value = False

        use_case.execute(rut="12345678-9", password="secreta123", contexto=contexto)

        registro = servicio_auditoria_mock.registrar_autenticacion.call_args.kwargs
        assert "password" not in registro
        assert registro["detalle"] == "Credenciales inválidas"
        assert "secreta123" not in str(registro)

    def test_login_password_incorrecta(self, use_case, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(password_hash="hash_valido")
        repositorio_mock.buscar.return_value = usuario
        auth_service_mock.verificar_password.return_value = False

        resultado = use_case.execute(rut="12345678-9", password="wrong_password", contexto=crear_contexto_peticion_mock())

        assert resultado is None

    def test_login_usuario_deshabilitado(self, use_case, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(habilitado=False)
        repositorio_mock.buscar.return_value = usuario

        resultado = use_case.execute(rut="12345678-9", password="password123", contexto=crear_contexto_peticion_mock())

        assert resultado is None

    def test_login_usuario_eliminado(self, use_case, repositorio_mock, auth_service_mock):
        usuario = crear_usuario_mock(eliminado=True)
        repositorio_mock.buscar.return_value = usuario

        resultado = use_case.execute(rut="12345678-9", password="password123", contexto=crear_contexto_peticion_mock())

        assert resultado is None

    def test_login_sin_password_hash(self, use_case, repositorio_mock):
        usuario = crear_usuario_mock(password_hash=None)
        repositorio_mock.buscar.return_value = usuario

        resultado = use_case.execute(rut="12345678-9", password="password123", contexto=crear_contexto_peticion_mock())

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

        use_case.execute(rut="12345678-9", password="password123", contexto=crear_contexto_peticion_mock())

        call_args = auth_service_mock.crear_access_token.call_args[0][0]
        assert "rut" in call_args
        assert "codigo_roles" in call_args
        assert "codigo_permisos" in call_args
        assert "VER_USUARIOS" in call_args["codigo_permisos"]
        assert "CREAR_PROSPECTOS" in call_args["codigo_permisos"]
