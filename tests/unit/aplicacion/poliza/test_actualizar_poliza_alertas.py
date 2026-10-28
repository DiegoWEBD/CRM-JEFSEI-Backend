from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import GenerarAlertaRenovacionPolizaUseCase
from app.aplicacion.poliza.use_cases.actualizar_poliza import ActualizarPolizaUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from tests.factories.notificacion_factory import crear_notificacion_mock

MODULO = 'app.aplicacion.poliza.use_cases.actualizar_poliza'

FIN_VIGENCIA = datetime(2026, 12, 31, 0, 0, 0, tzinfo=timezone.utc)


class _Usuario:
    def __init__(self, rut: str = '11111111-1'):
        self.rut = rut


def _use_case(fin_vigencia_guardada=FIN_VIGENCIA, autorizado=True):
    repo_polizas = MagicMock(spec=RepositorioPolizas)
    poliza = MagicMock(spec=Poliza)
    poliza.fin_vigencia = fin_vigencia_guardada
    repo_polizas.buscar.return_value = poliza

    authorization_service = MagicMock(spec=AuthorizationService)
    authorization_service.usuario_puede_actualizar_poliza.return_value = autorizado

    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.eliminar_renovacion.return_value = ['11111111-1']

    generar_alerta_renovacion = MagicMock(spec=GenerarAlertaRenovacionPolizaUseCase)
    generar_alerta_renovacion.ejecutar.return_value = []

    uc = ActualizarPolizaUseCase(
        repo_polizas, authorization_service, servicio_alertas, generar_alerta_renovacion
    )
    return uc, repo_polizas, servicio_alertas, generar_alerta_renovacion


def _ejecutar(uc, fin_vigencia=FIN_VIGENCIA):
    uc.ejecutar(
        numero_poliza='POL-001',
        usuario=_Usuario(),
        tipo='nueva',
        prima_neta=100.0,
        comision_corredora_pct=10.0,
        fecha_emision=None,
        inicio_vigencia=None,
        fin_vigencia=fin_vigencia,
        id_company=None,
    )


@pytest.mark.unit
class TestActualizarPolizaAlertasRenovacion:

    def test_poliza_no_encontrada(self):
        uc, repo_polizas, _, _ = _use_case()
        repo_polizas.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            _ejecutar(uc)

    def test_sin_permiso_no_actualiza(self):
        uc, repo_polizas, _, _ = _use_case(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            _ejecutar(uc)

        repo_polizas.actualizar.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_cambiar_fin_vigencia_elimina_las_de_la_vigencia_anterior(self, hub_mock):
        uc, _, servicio_alertas, generar = _use_case()

        _ejecutar(uc, fin_vigencia=datetime(2027, 1, 31, tzinfo=timezone.utc))

        servicio_alertas.eliminar_renovacion.assert_called_once_with('POL-001')
        # Se re-evalúa al tiro: las alertas de la fecha nueva se crean ahora y
        # no se esperan a la próxima corrida del scheduler.
        generar.ejecutar.assert_called_once()
        args = generar.ejecutar.call_args.args
        assert args[0] == 'POL-001'
        assert isinstance(args[1], datetime)

    @patch(f'{MODULO}.hub')
    def test_crea_alertas_de_la_vigencia_nueva_y_publica(self, hub_mock):
        uc, _, servicio_alertas, generar = _use_case()
        servicio_alertas.eliminar_renovacion.return_value = ['11111111-1']
        generar.ejecutar.return_value = [
            crear_notificacion_mock(id=None, rut_usuario='22222222-2', codigo_tipo='RENOVACION_GESTION_PENDIENTE'),
        ]

        _ejecutar(uc, fin_vigencia=datetime(2027, 1, 31, tzinfo=timezone.utc))

        hub_mock.publicar_desde_hilo.assert_called_once()
        destinatarios = set(hub_mock.publicar_desde_hilo.call_args.args[0])
        payload = hub_mock.publicar_desde_hilo.call_args.args[1]
        assert destinatarios == {'11111111-1', '22222222-2'}
        assert payload == {
            'evento': 'notificaciones_actualizadas',
            'motivo': 'alertas_renovacion_actualizadas',
        }

    @patch(f'{MODULO}.hub')
    def test_fin_vigencia_sin_cambio_no_toca_alertas(self, hub_mock):
        uc, _, servicio_alertas, generar = _use_case()

        _ejecutar(uc, fin_vigencia=FIN_VIGENCIA)

        servicio_alertas.eliminar_renovacion.assert_not_called()
        generar.ejecutar.assert_not_called()
        hub_mock.publicar_desde_hilo.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_mismo_instante_en_otra_zona_horaria_no_toca_alertas(self, hub_mock):
        """El mismo instante expresado como datetime naive no cuenta como cambio."""
        uc, _, servicio_alertas, generar = _use_case()

        _ejecutar(uc, fin_vigencia=datetime(2026, 12, 31, 0, 0, 0))

        servicio_alertas.eliminar_renovacion.assert_not_called()
        generar.ejecutar.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_quitar_fin_vigencia_tambien_elimina_y_reevalua(self, hub_mock):
        uc, _, servicio_alertas, generar = _use_case()

        _ejecutar(uc, fin_vigencia=None)

        servicio_alertas.eliminar_renovacion.assert_called_once_with('POL-001')
        generar.ejecutar.assert_called_once()

    @patch(f'{MODULO}.hub')
    def test_sin_alertas_eliminadas_ni_creadas_no_publica(self, hub_mock):
        uc, _, servicio_alertas, generar = _use_case()
        servicio_alertas.eliminar_renovacion.return_value = []
        generar.ejecutar.return_value = []

        _ejecutar(uc, fin_vigencia=datetime(2027, 1, 31, tzinfo=timezone.utc))

        hub_mock.publicar_desde_hilo.assert_not_called()
