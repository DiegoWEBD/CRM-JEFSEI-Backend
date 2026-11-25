import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.usuario.use_cases.cambiar_password import (
    EVENTO_CAMBIO_CONTRASENA,
    CambiarPasswordUseCase,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.usuario_factory import crear_usuario_mock

PASSWORD_ACTUAL = 'PasswordActual1'
PASSWORD_NUEVA = 'PasswordNueva1'


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioUsuarios)


@pytest.fixture
def auth_service_mock():
    service = MagicMock(spec=AuthenticationService)
    service.verificar_password.return_value = True
    service.hash_password.return_value = 'hashed_password_nueva'
    return service


@pytest.fixture
def servicio_auditoria_mock():
    return MagicMock(spec=ServicioAuditoria)


@pytest.fixture
def contexto():
    return ContextoPeticion(ip_origen='127.0.0.1', user_agent='pytest', id_peticion='test-1')


@pytest.fixture
def sesion_id_actual():
    return uuid4()


@pytest.mark.unit
class TestCambiarPasswordUseCase:

    def test_cambio_exitoso(
        self, repositorio_mock, auth_service_mock, servicio_auditoria_mock,
        contexto, sesion_id_actual
    ):
        repositorio_mock.buscar.return_value = crear_usuario_mock()
        repositorio_mock.actualizar_password_hash.return_value = True

        uc = CambiarPasswordUseCase(
            repositorio_mock, auth_service_mock, servicio_auditoria_mock
        )
        resultado = uc.ejecutar(
            rut='12345678-9',
            password_actual=PASSWORD_ACTUAL,
            password_nueva=PASSWORD_NUEVA,
            sesion_id_actual=sesion_id_actual,
            contexto=contexto,
        )

        assert resultado is True
        auth_service_mock.hash_password.assert_called_once_with(PASSWORD_NUEVA)
        repositorio_mock.actualizar_password_hash.assert_called_once_with(
            '12345678-9', 'hashed_password_nueva'
        )
        auth_service_mock.revocar_todas_las_sesiones_excepto.assert_called_once_with(
            '12345678-9', sesion_id_actual, motivo='password_change'
        )
        servicio_auditoria_mock.registrar_autenticacion.assert_called_once()
        assert (
            servicio_auditoria_mock.registrar_autenticacion.call_args.kwargs['evento']
            == EVENTO_CAMBIO_CONTRASENA
        )

    def test_password_actual_incorrecta(
        self, repositorio_mock, auth_service_mock, servicio_auditoria_mock,
        contexto, sesion_id_actual
    ):
        repositorio_mock.buscar.return_value = crear_usuario_mock()
        auth_service_mock.verificar_password.return_value = False

        uc = CambiarPasswordUseCase(
            repositorio_mock, auth_service_mock, servicio_auditoria_mock
        )

        with pytest.raises(
            DatoInvalidoException, match='La contraseña actual no es correcta'
        ):
            uc.ejecutar(
                rut='12345678-9',
                password_actual='Cualquiera123',
                password_nueva=PASSWORD_NUEVA,
                sesion_id_actual=sesion_id_actual,
                contexto=contexto,
            )

        repositorio_mock.actualizar_password_hash.assert_not_called()
        auth_service_mock.revocar_todas_las_sesiones_excepto.assert_not_called()
        servicio_auditoria_mock.registrar_autenticacion.assert_not_called()

    def test_nueva_igual_a_actual_es_rechazada(
        self, repositorio_mock, auth_service_mock, servicio_auditoria_mock,
        contexto, sesion_id_actual
    ):
        repositorio_mock.buscar.return_value = crear_usuario_mock()

        uc = CambiarPasswordUseCase(
            repositorio_mock, auth_service_mock, servicio_auditoria_mock
        )

        with pytest.raises(
            DatoInvalidoException, match='no puede ser igual a la actual'
        ):
            uc.ejecutar(
                rut='12345678-9',
                password_actual=PASSWORD_ACTUAL,
                password_nueva=PASSWORD_ACTUAL,
                sesion_id_actual=sesion_id_actual,
                contexto=contexto,
            )

        repositorio_mock.actualizar_password_hash.assert_not_called()
        auth_service_mock.revocar_todas_las_sesiones_excepto.assert_not_called()

    def test_nueva_debil_es_rechazada(
        self, repositorio_mock, auth_service_mock, servicio_auditoria_mock,
        contexto, sesion_id_actual
    ):
        repositorio_mock.buscar.return_value = crear_usuario_mock()

        uc = CambiarPasswordUseCase(
            repositorio_mock, auth_service_mock, servicio_auditoria_mock
        )

        with pytest.raises(DatoInvalidoException, match='al menos 12 caracteres'):
            uc.ejecutar(
                rut='12345678-9',
                password_actual=PASSWORD_ACTUAL,
                password_nueva='corta',
                sesion_id_actual=sesion_id_actual,
                contexto=contexto,
            )

        auth_service_mock.hash_password.assert_not_called()
        repositorio_mock.actualizar_password_hash.assert_not_called()
        auth_service_mock.revocar_todas_las_sesiones_excepto.assert_not_called()

    def test_usuario_no_existe(
        self, repositorio_mock, auth_service_mock, servicio_auditoria_mock,
        contexto, sesion_id_actual
    ):
        repositorio_mock.buscar.return_value = None

        uc = CambiarPasswordUseCase(
            repositorio_mock, auth_service_mock, servicio_auditoria_mock
        )

        with pytest.raises(RecursoNoEncontradoException, match='El usuario no existe'):
            uc.ejecutar(
                rut='99999999-9',
                password_actual=PASSWORD_ACTUAL,
                password_nueva=PASSWORD_NUEVA,
                sesion_id_actual=sesion_id_actual,
                contexto=contexto,
            )

    def test_actualizacion_fallida_no_revoca_sesiones(
        self, repositorio_mock, auth_service_mock, servicio_auditoria_mock,
        contexto, sesion_id_actual
    ):
        repositorio_mock.buscar.return_value = crear_usuario_mock()
        repositorio_mock.actualizar_password_hash.return_value = False

        uc = CambiarPasswordUseCase(
            repositorio_mock, auth_service_mock, servicio_auditoria_mock
        )
        resultado = uc.ejecutar(
            rut='12345678-9',
            password_actual=PASSWORD_ACTUAL,
            password_nueva=PASSWORD_NUEVA,
            sesion_id_actual=sesion_id_actual,
            contexto=contexto,
        )

        assert resultado is False
        auth_service_mock.revocar_todas_las_sesiones_excepto.assert_not_called()
        servicio_auditoria_mock.registrar_autenticacion.assert_not_called()
