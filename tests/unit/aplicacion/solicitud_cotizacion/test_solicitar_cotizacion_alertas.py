from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion import (
    SolicitarCotizacionUseCase,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import (
    RepositorioSolicitudesCotizacion,
)

MODULO = 'app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion'


def _request_mock(tipo='generico'):
    return MagicMock(
        tipo=tipo,
        prioridad='ALTA',
        observaciones=None,
        monto_asegurado=100.0,
    )


def _use_case():
    repo_solicitudes = MagicMock(spec=RepositorioSolicitudesCotizacion)
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.buscar.return_value = MagicMock(id=42)
    authorization = MagicMock()
    authorization.usuario_puede_solicitar_cotizacion.return_value = True
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas.return_value = ['11111111-1']
    uc = SolicitarCotizacionUseCase(
        repo_solicitudes,
        repo_procesos,
        authorization,
        repo_notificaciones,
        servicio_alertas,
    )
    return uc, repo_solicitudes, servicio_alertas


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestSolicitarCotizacionAlertas:

    def test_tras_registrar_marca_alertas_sla_del_proceso(self, mock_hub):
        uc, repo_solicitudes, servicio_alertas = _use_case()

        uc.ejecutar(id_proceso_comercial=42, request=_request_mock(), usuario=MagicMock(rut='99999999-9'))

        repo_solicitudes.nueva_solicitud.assert_called_once()
        servicio_alertas.marcar_leidas.assert_called_once()
        args = servicio_alertas.marcar_leidas.call_args.args
        assert args[0] == 42
        assert args[1] == TIPOS_ALERTA_SLA
        assert isinstance(args[2], datetime)

    def test_publica_con_motivo_alertas_leidas_cambio_estado(self, mock_hub):
        uc, _, _ = _use_case()

        uc.ejecutar(id_proceso_comercial=42, request=_request_mock(), usuario=MagicMock(rut='99999999-9'))

        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    def test_sin_destinatarios_no_publica(self, mock_hub):
        uc, _, servicio_alertas = _use_case()
        servicio_alertas.marcar_leidas.return_value = []

        uc.ejecutar(id_proceso_comercial=42, request=_request_mock(), usuario=MagicMock(rut='99999999-9'))

        mock_hub.publicar_desde_hilo.assert_not_called()
