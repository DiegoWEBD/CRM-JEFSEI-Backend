from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.cotizacion.use_cases.registrar_cotizacion_a_solicitud import (
    RegistrarCotizacionASolicitudUseCase,
)
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)

MODULO = 'app.aplicacion.cotizacion.use_cases.registrar_cotizacion_a_solicitud'


def _use_case(proceso=None):
    repo_companies = MagicMock()
    repo_solicitudes = MagicMock()
    repo_solicitudes.existe_solicitud.return_value = True
    repo_cotizaciones = MagicMock()
    authorization = MagicMock()
    authorization.usuario_puede_ver_solicitud_cotizacion.return_value = True
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.buscar_por_solicitud_cotizacion.return_value = proceso
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas.return_value = ['11111111-1']
    uc = RegistrarCotizacionASolicitudUseCase(
        repo_companies,
        repo_solicitudes,
        repo_cotizaciones,
        authorization,
        repo_procesos,
        repo_notificaciones,
        servicio_alertas,
    )
    return uc, repo_cotizaciones, repo_procesos, servicio_alertas


def _cotizacion_mock():
    cotizacion = MagicMock()
    cotizacion.company.id = 1
    return cotizacion


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestRegistrarCotizacionASolicitudAlertas:

    def test_con_proceso_resuelto_marca_alertas_sla(self, mock_hub):
        uc, repo_cotizaciones, repo_procesos, servicio_alertas = _use_case(
            proceso=MagicMock(id=42)
        )

        uc.ejecutar(rut_usuario='99999999-9', id_solicitud=3, cotizacion=_cotizacion_mock())

        repo_cotizaciones.registrar_cotizacion_a_solicitud.assert_called_once()
        repo_procesos.buscar_por_solicitud_cotizacion.assert_called_once_with(3)
        args = servicio_alertas.marcar_leidas.call_args.args
        assert args[0] == 42
        assert args[1] == TIPOS_ALERTA_SLA
        assert isinstance(args[2], datetime)
        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    def test_sin_proceso_resuelto_no_marca_ni_publica(self, mock_hub):
        uc, _, repo_procesos, servicio_alertas = _use_case(proceso=None)

        uc.ejecutar(rut_usuario='99999999-9', id_solicitud=3, cotizacion=_cotizacion_mock())

        repo_procesos.buscar_por_solicitud_cotizacion.assert_called_once_with(3)
        servicio_alertas.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_sin_destinatarios_no_publica(self, mock_hub):
        uc, _, _, servicio_alertas = _use_case(proceso=MagicMock(id=42))
        servicio_alertas.marcar_leidas.return_value = []

        uc.ejecutar(rut_usuario='99999999-9', id_solicitud=3, cotizacion=_cotizacion_mock())

        mock_hub.publicar_desde_hilo.assert_not_called()
