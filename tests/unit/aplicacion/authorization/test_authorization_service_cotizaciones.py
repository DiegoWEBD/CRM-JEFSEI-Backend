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
class TestUsuarioPuedeRegistrarCotizacion:

    def test_permiso_y_ownership_delegan_al_repositorio(self):
        service = _service()
        service.authorization_repository.usuario_puede_registrar_cotizacion.return_value = True

        resultado = service.usuario_puede_registrar_cotizacion('12345678-9', 7)

        assert resultado is True
        service.authorization_repository.usuario_puede_registrar_cotizacion.assert_called_once_with(
            '12345678-9', 7
        )

    def test_denegacion_delega_al_repositorio(self):
        service = _service()
        service.authorization_repository.usuario_puede_registrar_cotizacion.return_value = False

        resultado = service.usuario_puede_registrar_cotizacion('99999999-9', 7)

        assert resultado is False
        service.authorization_repository.usuario_puede_registrar_cotizacion.assert_called_once_with(
            '99999999-9', 7
        )
