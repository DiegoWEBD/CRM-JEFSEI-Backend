from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.archivo.servicios.servicio_archivos import ServicioArchivos
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.solicitud_cotizacion.use_cases.eliminar_solicitud_cotizacion import (
    EliminarSolicitudCotizacionUseCase,
)
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.exceptions.conflicto_en_accion_exception import (
    ConflictoEnAccionException,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import (
    HistorialEstadoProcesoComercial,
)
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import (
    RepositorioHistorialEstadoProcesosComerciales,
)
from app.dominio.notificacion.repositorio_notificaciones import (
    RepositorioNotificaciones,
)
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import (
    RepositorioSolicitudesCotizacion,
)
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock

MODULO = 'app.aplicacion.solicitud_cotizacion.use_cases.eliminar_solicitud_cotizacion'


def _cotizacion_mock(nombre_archivo='cotizacion_1.pdf'):
    cot = MagicMock()
    cot.nombre_archivo = nombre_archivo
    return cot


def _use_case(
    proceso=None,
    existe_solicitud=True,
    autorizado=True,
    cotizaciones=None,
    destinatarios=None,
):
    if cotizaciones is None:
        cotizaciones = [_cotizacion_mock(), _cotizacion_mock('cotizacion_2.pdf')]
    if destinatarios is None:
        destinatarios = ['11111111-1']
    if proceso is None:
        proceso = crear_proceso_comercial_mock(id=42, cerrado=False)

    repo_solicitudes = MagicMock(spec=RepositorioSolicitudesCotizacion)
    repo_solicitudes.existe_solicitud.return_value = existe_solicitud

    repo_cotizaciones = MagicMock(spec=RepositorioCotizaciones)
    repo_cotizaciones.obtener_por_solicitud.return_value = cotizaciones

    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.buscar_por_solicitud_cotizacion.return_value = proceso

    repo_historial = MagicMock(spec=RepositorioHistorialEstadoProcesosComerciales)

    authorization = MagicMock(spec=AuthorizationService)
    authorization.usuario_puede_eliminar_solicitud_cotizacion.return_value = autorizado

    repo_notificaciones = MagicMock(spec=RepositorioNotificaciones)

    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.marcar_leidas.return_value = destinatarios

    servicio_archivos = MagicMock(spec=ServicioArchivos)

    uc = EliminarSolicitudCotizacionUseCase(
        repositorio_solicitudes_cotizacion=repo_solicitudes,
        repositorio_cotizaciones=repo_cotizaciones,
        repositorio_procesos_comerciales=repo_procesos,
        repositorio_historial=repo_historial,
        authorization_service=authorization,
        repositorio_notificaciones=repo_notificaciones,
        servicio_alertas=servicio_alertas,
        servicio_archivos=servicio_archivos,
    )
    return uc, repo_solicitudes, repo_cotizaciones, repo_procesos, repo_historial, servicio_alertas, servicio_archivos


@pytest.mark.unit
@patch(f'{MODULO}.hub')
class TestEliminarSolicitudCotizacion:

    def test_elimina_solicitud_y_archivos(self, mock_hub):
        uc, repo_solicitudes, repo_cotizaciones, _, _, _, servicio_archivos = _use_case()

        uc.ejecutar(id_solicitud=1, rut_usuario='99999999-9')

        repo_solicitudes.eliminar.assert_called_once_with(1)
        repo_cotizaciones.obtener_por_solicitud.assert_called_once_with(1)
        assert servicio_archivos.eliminar.call_count == 2
        servicio_archivos.eliminar.assert_any_call('documentos/cotizaciones', 'cotizacion_1.pdf')
        servicio_archivos.eliminar.assert_any_call('documentos/cotizaciones', 'cotizacion_2.pdf')

    def test_registra_historial_con_estado_solicitud_cotizacion_eliminada(self, mock_hub):
        uc, _, _, _, repo_historial, _, _ = _use_case()

        uc.ejecutar(id_solicitud=1, rut_usuario='99999999-9')

        repo_historial.registrar.assert_called_once()
        historial = repo_historial.registrar.call_args.args[0]
        assert isinstance(historial, HistorialEstadoProcesoComercial)
        assert historial.codigo_estado == 'SOLICITUD_COTIZACION_ELIMINADA'
        assert historial.id_proceso_comercial == 42
        assert historial.rut_registrado_por == '99999999-9'

    def test_marca_alertas_sla_y_publica_hub(self, mock_hub):
        uc, _, _, _, _, servicio_alertas, _ = _use_case()

        uc.ejecutar(id_solicitud=1, rut_usuario='99999999-9')

        args = servicio_alertas.marcar_leidas.call_args.args
        assert args[0] == 42
        assert args[1] == TIPOS_ALERTA_SLA
        assert isinstance(args[2], datetime)
        assert args[2].tzinfo is not None
        mock_hub.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1'],
            {'evento': 'notificaciones_actualizadas', 'motivo': 'alertas_leidas_cambio_estado'},
        )

    def test_sin_destinatarios_no_publica(self, mock_hub):
        uc, _, _, _, _, _, _ = _use_case(destinatarios=[])

        uc.ejecutar(id_solicitud=1, rut_usuario='99999999-9')

        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_solicitud_no_encontrada_lanza_excepcion(self, mock_hub):
        uc, _, _, _, _, servicio_alertas, _ = _use_case(existe_solicitud=False)

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_solicitud=99, rut_usuario='99999999-9')

        servicio_alertas.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_usuario_no_autorizado_lanza_excepcion(self, mock_hub):
        uc, _, _, _, _, servicio_alertas, _ = _use_case(autorizado=False)

        with pytest.raises(UsuarioNoAutorizadoException):
            uc.ejecutar(id_solicitud=1, rut_usuario='00000000-0')

        servicio_alertas.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_proceso_no_encontrado_lanza_excepcion(self, mock_hub):
        uc, _, _, repo_procesos, _, servicio_alertas, _ = _use_case()
        repo_procesos.buscar_por_solicitud_cotizacion.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            uc.ejecutar(id_solicitud=1, rut_usuario='99999999-9')

        servicio_alertas.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_proceso_cerrado_lanza_excepcion(self, mock_hub):
        proceso_cerrado = crear_proceso_comercial_mock(id=42, cerrado=True)
        uc, _, _, _, repo_historial, servicio_alertas, _ = _use_case(proceso=proceso_cerrado)

        with pytest.raises(ConflictoEnAccionException):
            uc.ejecutar(id_solicitud=1, rut_usuario='99999999-9')

        repo_historial.registrar.assert_not_called()
        servicio_alertas.marcar_leidas.assert_not_called()
        mock_hub.publicar_desde_hilo.assert_not_called()

    def test_cotizaciones_sin_archivo_no_intenta_eliminar(self, mock_hub):
        cot = _cotizacion_mock(nombre_archivo=None)
        uc, _, _, _, _, _, servicio_archivos = _use_case(cotizaciones=[cot])

        uc.ejecutar(id_solicitud=1, rut_usuario='99999999-9')

        servicio_archivos.eliminar.assert_not_called()