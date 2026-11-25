from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService


def _service():
    return AuthorizationService(
        authorization_repository=MagicMock(),
        repositorio_prospectos=MagicMock(),
        repositorio_usuarios=MagicMock(),
        repositorio_procesos_comerciales=MagicMock(),
        repositorio_solicitudes_cotizacion=MagicMock(),
    )


@pytest.mark.unit
class TestUsuarioPuedeCrearPlanPago:

    def test_delega_al_repositorio(self):
        service = _service()
        service.authorization_repository.usuario_puede_crear_plan_pago.return_value = True

        resultado = service.usuario_puede_crear_plan_pago('12345678-9', 'POL-001')

        assert resultado is True
        service.authorization_repository.usuario_puede_crear_plan_pago.assert_called_once_with(
            '12345678-9', 'POL-001'
        )

    def test_denegacion_delega_al_repositorio(self):
        service = _service()
        service.authorization_repository.usuario_puede_crear_plan_pago.return_value = False

        resultado = service.usuario_puede_crear_plan_pago('99999999-9', 'POL-001')

        assert resultado is False


@pytest.mark.unit
class TestUsuarioPuedeCancelarPoliza:

    def test_delega_al_repositorio(self):
        service = _service()
        service.authorization_repository.usuario_puede_cancelar_poliza.return_value = True

        resultado = service.usuario_puede_cancelar_poliza('12345678-9', 'POL-001')

        assert resultado is True
        service.authorization_repository.usuario_puede_cancelar_poliza.assert_called_once_with(
            '12345678-9', 'POL-001'
        )

    def test_denegacion_delega_al_repositorio(self):
        service = _service()
        service.authorization_repository.usuario_puede_cancelar_poliza.return_value = False

        resultado = service.usuario_puede_cancelar_poliza('99999999-9', 'POL-001')

        assert resultado is False


@pytest.mark.unit
class TestUsuarioPuedeReactivarPoliza:

    def test_delega_al_repositorio(self):
        service = _service()
        service.authorization_repository.usuario_puede_reactivar_poliza.return_value = True

        resultado = service.usuario_puede_reactivar_poliza('12345678-9', 'POL-001')

        assert resultado is True
        service.authorization_repository.usuario_puede_reactivar_poliza.assert_called_once_with(
            '12345678-9', 'POL-001'
        )

    def test_denegacion_delega_al_repositorio(self):
        service = _service()
        service.authorization_repository.usuario_puede_reactivar_poliza.return_value = False

        resultado = service.usuario_puede_reactivar_poliza('99999999-9', 'POL-001')

        assert resultado is False
