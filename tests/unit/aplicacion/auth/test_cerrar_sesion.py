from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.aplicacion.auth.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria
from tests.factories.auditoria_factory import crear_contexto_peticion_mock


@pytest.fixture
def servicio_auditoria_mock():
    return MagicMock(spec=ServicioAuditoria)


@pytest.fixture
def auth_service_mock():
    return MagicMock(spec=AuthenticationService)


@pytest.fixture
def use_case(servicio_auditoria_mock, auth_service_mock):
    return CerrarSesionUseCase(servicio_auditoria_mock, auth_service_mock)


@pytest.mark.unit
class TestCerrarSesionUseCase:

    def test_registra_evento_logout_y_revoca_sesion(self, use_case, servicio_auditoria_mock, auth_service_mock):
        contexto = crear_contexto_peticion_mock()
        sesion_id = uuid4()

        use_case.ejecutar(rut="12345678-9", nombre="Juan Perez", sesion_id=sesion_id, contexto=contexto)

        auth_service_mock.revocar_sesion.assert_called_once_with(sesion_id, motivo='logout')

        servicio_auditoria_mock.registrar_autenticacion.assert_called_once()
        kwargs = servicio_auditoria_mock.registrar_autenticacion.call_args.kwargs
        assert kwargs["evento"] == EventoAuditoria.LOGOUT
        assert kwargs["resultado"] == ResultadoAuditoria.EXITO
        assert kwargs["rut_usuario"] == "12345678-9"
        assert kwargs["nombre_usuario"] == "Juan Perez"
        assert kwargs["contexto"] == contexto

    def test_logout_sin_nombre_no_falla(self, use_case, servicio_auditoria_mock):
        contexto = crear_contexto_peticion_mock()

        use_case.ejecutar(rut="12345678-9", nombre=None, sesion_id=None, contexto=contexto)

        kwargs = servicio_auditoria_mock.registrar_autenticacion.call_args.kwargs
        assert kwargs["nombre_usuario"] is None

    def test_logout_sin_sesion_id_solo_audita(self, use_case, servicio_auditoria_mock, auth_service_mock):
        contexto = crear_contexto_peticion_mock()

        use_case.ejecutar(rut="12345678-9", nombre="Juan", sesion_id=None, contexto=contexto)

        auth_service_mock.revocar_sesion.assert_not_called()
        servicio_auditoria_mock.registrar_autenticacion.assert_called_once()
