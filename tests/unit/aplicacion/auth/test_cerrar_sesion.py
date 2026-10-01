from unittest.mock import MagicMock

import pytest

from app.aplicacion.auth.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria
from tests.factories.auditoria_factory import crear_contexto_peticion_mock


@pytest.fixture
def servicio_auditoria_mock():
    return MagicMock(spec=ServicioAuditoria)


@pytest.fixture
def use_case(servicio_auditoria_mock):
    return CerrarSesionUseCase(servicio_auditoria_mock)


@pytest.mark.unit
class TestCerrarSesionUseCase:

    def test_registra_evento_logout(self, use_case, servicio_auditoria_mock):
        contexto = crear_contexto_peticion_mock()

        use_case.ejecutar(rut="12345678-9", nombre="Juan Perez", contexto=contexto)

        servicio_auditoria_mock.registrar_autenticacion.assert_called_once()
        kwargs = servicio_auditoria_mock.registrar_autenticacion.call_args.kwargs
        assert kwargs["evento"] == EventoAuditoria.LOGOUT
        assert kwargs["resultado"] == ResultadoAuditoria.EXITO
        assert kwargs["rut_usuario"] == "12345678-9"
        assert kwargs["nombre_usuario"] == "Juan Perez"
        assert kwargs["contexto"] == contexto

    def test_logout_sin_nombre_no_falla(self, use_case, servicio_auditoria_mock):
        contexto = crear_contexto_peticion_mock()

        use_case.ejecutar(rut="12345678-9", nombre=None, contexto=contexto)

        kwargs = servicio_auditoria_mock.registrar_autenticacion.call_args.kwargs
        assert kwargs["nombre_usuario"] is None
