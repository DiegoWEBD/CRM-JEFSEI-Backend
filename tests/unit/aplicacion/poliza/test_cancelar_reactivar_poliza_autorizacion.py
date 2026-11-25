from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.poliza.use_cases.cancelar_poliza import CancelarPolizaUseCase
from app.aplicacion.poliza.use_cases.reactivar_poliza import ReactivarPolizaUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas

MODULO_CANCELAR = 'app.aplicacion.poliza.use_cases.cancelar_poliza'
MODULO_REACTIVAR = 'app.aplicacion.poliza.use_cases.reactivar_poliza'

MENSAJE_NO_ENCONTRADA = 'Póliza POL-001 no encontrada'

USUARIO = MagicMock(rut='99999999-9')


def _poliza_mock(estado=EstadoPoliza.VIGENTE):
    poliza = MagicMock(spec=Poliza)
    poliza.estado = estado
    return poliza


def _cancelar_use_case(poliza, puede_cancelar):
    repo_polizas = MagicMock(spec=RepositorioPolizas)
    repo_polizas.buscar.return_value = poliza
    authorization = MagicMock()
    authorization.usuario_puede_cancelar_poliza.return_value = puede_cancelar
    servicio_alertas = MagicMock()
    servicio_alertas.eliminar_renovacion.return_value = []
    return CancelarPolizaUseCase(repo_polizas, authorization, servicio_alertas), repo_polizas, authorization


def _reactivar_use_case(poliza, puede_reactivar):
    repo_polizas = MagicMock(spec=RepositorioPolizas)
    repo_polizas.buscar.return_value = poliza
    authorization = MagicMock()
    authorization.usuario_puede_reactivar_poliza.return_value = puede_reactivar
    generar = MagicMock()
    generar.ejecutar.return_value = []
    return ReactivarPolizaUseCase(repo_polizas, authorization, generar), repo_polizas, authorization


@pytest.mark.unit
@patch(f'{MODULO_CANCELAR}.hub')
class TestCancelarPolizaAutorizacion:

    def test_inexistente_y_denegada_responden_404_identico(self, hub_mock):
        """Política anti-oráculo: la denegación de ownership responde 404 con el
        mismo mensaje que una póliza que no existe."""
        uc_inexistente, _, _ = _cancelar_use_case(None, puede_cancelar=True)
        uc_denegado, _, _ = _cancelar_use_case(_poliza_mock(), puede_cancelar=False)

        with pytest.raises(RecursoNoEncontradoException) as exc_inexistente:
            uc_inexistente.ejecutar('POL-001', USUARIO)

        with pytest.raises(RecursoNoEncontradoException) as exc_denegado:
            uc_denegado.ejecutar('POL-001', USUARIO)

        assert str(exc_inexistente.value) == MENSAJE_NO_ENCONTRADA
        assert str(exc_denegado.value) == str(exc_inexistente.value)

    def test_denegada_no_toca_la_poliza(self, hub_mock):
        uc, repo_polizas, authorization = _cancelar_use_case(_poliza_mock(), puede_cancelar=False)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar('POL-001', USUARIO)

        authorization.usuario_puede_cancelar_poliza.assert_called_once_with('99999999-9', 'POL-001')
        repo_polizas.actualizar_cancelada.assert_not_called()
        hub_mock.publicar_desde_hilo.assert_not_called()

    def test_cancelar_con_ownership_procede(self, hub_mock):
        uc, repo_polizas, _ = _cancelar_use_case(_poliza_mock(), puede_cancelar=True)

        uc.ejecutar('POL-001', USUARIO)

        repo_polizas.actualizar_cancelada.assert_called_once_with('POL-001', True)


@pytest.mark.unit
@patch(f'{MODULO_REACTIVAR}.hub')
class TestReactivarPolizaAutorizacion:

    def test_inexistente_y_denegada_responden_404_identico(self, hub_mock):
        uc_inexistente, _, _ = _reactivar_use_case(None, puede_reactivar=True)
        uc_denegado, _, _ = _reactivar_use_case(
            _poliza_mock(estado=EstadoPoliza.CANCELADA), puede_reactivar=False
        )

        with pytest.raises(RecursoNoEncontradoException) as exc_inexistente:
            uc_inexistente.ejecutar('POL-001', USUARIO)

        with pytest.raises(RecursoNoEncontradoException) as exc_denegado:
            uc_denegado.ejecutar('POL-001', USUARIO)

        assert str(exc_inexistente.value) == MENSAJE_NO_ENCONTRADA
        assert str(exc_denegado.value) == str(exc_inexistente.value)

    def test_denegada_no_toca_la_poliza(self, hub_mock):
        uc, repo_polizas, authorization = _reactivar_use_case(
            _poliza_mock(estado=EstadoPoliza.CANCELADA), puede_reactivar=False
        )

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar('POL-001', USUARIO)

        authorization.usuario_puede_reactivar_poliza.assert_called_once_with('99999999-9', 'POL-001')
        repo_polizas.actualizar_cancelada.assert_not_called()
        hub_mock.publicar_desde_hilo.assert_not_called()

    def test_reactivar_con_ownership_procede(self, hub_mock):
        uc, repo_polizas, _ = _reactivar_use_case(
            _poliza_mock(estado=EstadoPoliza.CANCELADA), puede_reactivar=True
        )

        uc.ejecutar('POL-001', USUARIO)

        repo_polizas.actualizar_cancelada.assert_called_once_with('POL-001', False)
