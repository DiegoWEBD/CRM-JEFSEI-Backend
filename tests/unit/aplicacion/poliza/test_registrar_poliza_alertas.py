from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.poliza.use_cases.registrar_poliza_a_proceso_comercial import (
    RegistrarPolizaAProcesoComercialUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA

MODULO = 'app.aplicacion.poliza.use_cases.registrar_poliza_a_proceso_comercial'


def _use_case():
    repo_polizas = MagicMock()
    repo_polizas.buscar.return_value = None
    repo_procesos = MagicMock()
    repo_procesos.buscar.return_value = MagicMock(id=42)
    repo_companies = MagicMock()
    repo_companies.buscar.return_value = MagicMock(id=1)
    authorization = MagicMock()
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas.return_value = ['11111111-1']
    uc = RegistrarPolizaAProcesoComercialUseCase(
        repo_polizas,
        repo_procesos,
        repo_companies,
        authorization,
        repo_notificaciones,
        servicio_alertas,
    )
    return uc, repo_polizas, servicio_alertas


def _ejecutar(uc):
    return uc.ejecutar(
        id_proceso_comercial=42,
        numero_poliza='POL-001',
        tipo='INCENDIO',
        id_company=1,
        prima_neta=100.0,
        comision_corredora_pct=10.0,
        fecha_emision=None,
        inicio_vigencia=None,
        fin_vigencia=None,
        usuario=MagicMock(rut='99999999-9'),
    )


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestRegistrarPolizaAlertas:

    def test_tras_registrar_marca_alertas_sla_del_proceso(self, mock_hub):
        uc, repo_polizas, servicio_alertas = _use_case()

        _ejecutar(uc)

        repo_polizas.registrar_a_proceso_comercial.assert_called_once()
        args = servicio_alertas.marcar_leidas.call_args.args
        assert args[0] == 42
        assert args[1] == TIPOS_ALERTA_SLA
        assert isinstance(args[2], datetime)

    def test_publica_con_motivo_alertas_leidas_cambio_estado(self, mock_hub):
        uc, _, _ = _use_case()

        _ejecutar(uc)

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    def test_sin_destinatarios_no_publica(self, mock_hub):
        uc, _, servicio_alertas = _use_case()
        servicio_alertas.marcar_leidas.return_value = []

        _ejecutar(uc)

        mock_hub.publicar_desde_hilo.assert_not_called()
