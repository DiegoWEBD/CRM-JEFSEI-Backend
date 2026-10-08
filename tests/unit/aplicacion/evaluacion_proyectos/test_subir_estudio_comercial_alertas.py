from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest

from app.aplicacion.evaluacion_proyectos.use_cases.subir_estudio_comercial import (
    SubirEstudioComercialUseCase,
)
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)

MODULO = 'app.aplicacion.evaluacion_proyectos.use_cases.subir_estudio_comercial'


def _use_case(proceso=None):
    repo_estudios = MagicMock()
    repo_estudios.insertar.return_value = 5
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.buscar_por_solicitud_cotizacion.return_value = proceso
    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)
    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas.return_value = ['11111111-1']
    uc = SubirEstudioComercialUseCase(
        repo_estudios,
        repo_procesos,
        repo_notificaciones,
        servicio_alertas,
    )
    return uc, repo_estudios, repo_procesos, servicio_alertas


def _archivo_mock():
    archivo = MagicMock()
    archivo.file.read.return_value = b'%PDF-1.4'
    return archivo


@pytest.mark.unit
@patch(f'{MODULO}.os.makedirs')
@patch('builtins.open', new_callable=mock_open)
class TestSubirEstudioComercialAlertas:

    def test_tras_insertar_marca_alertas_sla_del_proceso(
        self, mock_abrir, mock_makedirs,
    ):
        uc, repo_estudios, repo_procesos, servicio_alertas = _use_case(proceso=MagicMock(id=42))

        uc.ejecutar(archivo=_archivo_mock(), id_solicitud=3, usuario=MagicMock(rut='99999999-9'))

        repo_estudios.insertar.assert_called_once()
        repo_procesos.buscar_por_solicitud_cotizacion.assert_called_once_with(3)
        args = servicio_alertas.marcar_leidas.call_args.args
        assert args[0] == 42
        assert args[1] == TIPOS_ALERTA_SLA
        assert isinstance(args[2], datetime)

    @patch(f'{MODULO}.hub')
    def test_publica_con_motivo_y_conserva_la_firma_publica(
        self, mock_hub, mock_abrir, mock_makedirs,
    ):
        uc, _, _, _ = _use_case(proceso=MagicMock(id=42))

        id_estudio, nombre_unico = uc.ejecutar(
            archivo=_archivo_mock(), id_solicitud=3, usuario=MagicMock(rut='99999999-9')
        )

        assert id_estudio == 5
        assert nombre_unico.endswith('.pdf')
        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    @patch(f'{MODULO}.hub')
    def test_sin_proceso_resuelto_no_marca_ni_publica(
        self, mock_hub, mock_abrir, mock_makedirs,
    ):
        uc, _, repo_procesos, servicio_alertas = _use_case(proceso=None)

        uc.ejecutar(archivo=_archivo_mock(), id_solicitud=3, usuario=MagicMock(rut='99999999-9'))

        repo_procesos.buscar_por_solicitud_cotizacion.assert_called_once_with(3)
        servicio_alertas.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_sin_destinatarios_no_publica(self, mock_hub, mock_abrir, mock_makedirs):
        uc, _, _, servicio_alertas = _use_case(proceso=MagicMock(id=42))
        servicio_alertas.marcar_leidas.return_value = []

        uc.ejecutar(archivo=_archivo_mock(), id_solicitud=3, usuario=MagicMock(rut='99999999-9'))

        mock_hub.publicar_desde_hilo.assert_not_called()
