from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import GenerarAlertaRenovacionPolizaUseCase
from app.aplicacion.poliza.use_cases.cancelar_poliza import CancelarPolizaUseCase
from app.aplicacion.poliza.use_cases.reactivar_poliza import ReactivarPolizaUseCase
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from tests.factories.notificacion_factory import crear_notificacion_mock

MODULO_CANCELAR = 'app.aplicacion.poliza.use_cases.cancelar_poliza'
MODULO_REACTIVAR = 'app.aplicacion.poliza.use_cases.reactivar_poliza'


def _poliza_mock(estado=EstadoPoliza.VIGENTE):
    poliza = MagicMock(spec=Poliza)
    poliza.estado = estado
    return poliza


def _cancelar_use_case(poliza=None):
    repo_polizas = MagicMock(spec=RepositorioPolizas)
    repo_polizas.buscar.return_value = poliza if poliza is not None else _poliza_mock()
    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.eliminar_renovacion.return_value = []
    uc = CancelarPolizaUseCase(repo_polizas, servicio_alertas)
    return uc, repo_polizas, servicio_alertas


def _reactivar_use_case(poliza=None):
    repo_polizas = MagicMock(spec=RepositorioPolizas)
    repo_polizas.buscar.return_value = (
        poliza if poliza is not None else _poliza_mock(estado=EstadoPoliza.CANCELADA)
    )
    generar = MagicMock(spec=GenerarAlertaRenovacionPolizaUseCase)
    generar.ejecutar.return_value = []
    uc = ReactivarPolizaUseCase(repo_polizas, generar)
    return uc, repo_polizas, generar


@pytest.mark.unit
@patch(f'{MODULO_CANCELAR}.hub')
class TestCancelarPolizaAlertasRenovacion:

    def test_cancelar_elimina_las_alertas_de_renovacion(self, hub_mock):
        """Una póliza cancelada no genera alertas: se eliminan las pendientes
        para que no queden huérfanas."""
        uc, repo_polizas, servicio_alertas = _cancelar_use_case()
        servicio_alertas.eliminar_renovacion.return_value = ['11111111-1']

        uc.ejecutar('POL-001')

        repo_polizas.actualizar_cancelada.assert_called_once_with('POL-001', True)
        servicio_alertas.eliminar_renovacion.assert_called_once_with('POL-001')
        hub_mock.publicar_desde_hilo.assert_called_once()
        payload = hub_mock.publicar_desde_hilo.call_args.args[1]
        assert payload == {
            'evento': 'notificaciones_actualizadas',
            'motivo': 'alertas_renovacion_actualizadas',
        }

    def test_cancelar_sin_alertas_no_publica(self, hub_mock):
        uc, _, servicio_alertas = _cancelar_use_case()
        servicio_alertas.eliminar_renovacion.return_value = []

        uc.ejecutar('POL-001')

        hub_mock.publicar_desde_hilo.assert_not_called()

    def test_poliza_no_encontrada(self, hub_mock):
        uc, repo_polizas, servicio_alertas = _cancelar_use_case(poliza=None)
        repo_polizas.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar('POL-404')

        servicio_alertas.eliminar_renovacion.assert_not_called()

    def test_ya_cancelada_no_toca_alertas(self, hub_mock):
        uc, _, servicio_alertas = _cancelar_use_case(
            poliza=_poliza_mock(estado=EstadoPoliza.CANCELADA)
        )

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar('POL-001')

        servicio_alertas.eliminar_renovacion.assert_not_called()


@pytest.mark.unit
@patch(f'{MODULO_REACTIVAR}.hub')
class TestReactivarPolizaAlertasRenovacion:

    def test_reactivar_reevalua_y_crea_las_alertas(self, hub_mock):
        """Las alertas (eliminadas al cancelarla) se re-crean al tiro si los
        hitos siguen aplicando, sin esperar al scheduler."""
        uc, repo_polizas, generar = _reactivar_use_case()
        generar.ejecutar.return_value = [
            crear_notificacion_mock(
                id=None, rut_usuario='11111111-1', codigo_tipo='RENOVACION_GESTION_PENDIENTE'
            ),
        ]

        uc.ejecutar('POL-001')

        repo_polizas.actualizar_cancelada.assert_called_once_with('POL-001', False)
        generar.ejecutar.assert_called_once()
        args = generar.ejecutar.call_args.args
        assert args[0] == 'POL-001'
        assert args[1] is not None
        hub_mock.publicar_desde_hilo.assert_called_once()
        assert set(hub_mock.publicar_desde_hilo.call_args.args[0]) == {'11111111-1'}
        payload = hub_mock.publicar_desde_hilo.call_args.args[1]
        assert payload == {
            'evento': 'notificaciones_actualizadas',
            'motivo': 'alertas_renovacion_actualizadas',
        }

    def test_reactivar_sin_alertas_creadas_no_publica(self, hub_mock):
        uc, _, generar = _reactivar_use_case()
        generar.ejecutar.return_value = []

        uc.ejecutar('POL-001')

        hub_mock.publicar_desde_hilo.assert_not_called()

    def test_poliza_no_encontrada(self, hub_mock):
        uc, repo_polizas, generar = _reactivar_use_case()
        repo_polizas.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar('POL-404')

        generar.ejecutar.assert_not_called()

    def test_no_cancelada_no_reevalua(self, hub_mock):
        uc, _, generar = _reactivar_use_case(poliza=_poliza_mock(estado=EstadoPoliza.VIGENTE))

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar('POL-001')

        generar.ejecutar.assert_not_called()
