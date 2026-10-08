from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.plan_pago.use_cases.crear_plan_pago import CrearPlanPagoUseCase
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_FECHA, TIPOS_ALERTA_SLA

MODULO = 'app.aplicacion.plan_pago.use_cases.crear_plan_pago'


def _use_case():
    repo_polizas = MagicMock()
    repo_polizas.buscar.return_value = MagicMock(numero_poliza='POL-001', id_proceso_comercial=42)
    repo_planes_pago = MagicMock()
    repo_planes_pago.buscar_plan_pago_poliza.return_value = None
    authorization = MagicMock()
    repo_procesos = MagicMock()
    repo_procesos.buscar.return_value = MagicMock(id=42)
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas.return_value = ['11111111-1']
    uc = CrearPlanPagoUseCase(
        repo_polizas,
        repo_planes_pago,
        authorization,
        repo_procesos,
        repo_notificaciones,
        servicio_alertas,
    )
    return uc, repo_planes_pago, repo_procesos, servicio_alertas


def _ejecutar(uc):
    return uc.ejecutar(
        numero_poliza='POL-001',
        fecha_primera_cuota=datetime(2026, 11, 1),
        numero_cuotas=3,
        usuario=MagicMock(rut='99999999-9'),
    )


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestCrearPlanPagoAlertas:

    def test_marca_sla_y_fecha_una_sola_vez_tras_ambas_transiciones(self, mock_hub):
        uc, repo_planes_pago, repo_procesos, servicio_alertas = _use_case()

        _ejecutar(uc)

        repo_planes_pago.registrar_plan_pago_poliza.assert_called_once()
        repo_procesos.cerrar.assert_called_once()
        servicio_alertas.marcar_leidas.assert_called_once()
        args = servicio_alertas.marcar_leidas.call_args.args
        assert args[0] == 42
        assert args[1] == TIPOS_ALERTA_SLA + TIPOS_ALERTA_FECHA
        assert isinstance(args[2], datetime)

    def test_publica_con_motivo_alertas_leidas_cambio_estado(self, mock_hub):
        uc, _, _, _ = _use_case()

        _ejecutar(uc)

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    def test_sin_destinatarios_no_publica(self, mock_hub):
        uc, _, _, servicio_alertas = _use_case()
        servicio_alertas.marcar_leidas.return_value = []

        _ejecutar(uc)

        mock_hub.publicar_desde_hilo.assert_not_called()
