from datetime import datetime, timezone

from app.aplicacion.archivo.servicios.servicio_archivos import ServicioArchivos
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.core.archivos import DIRECTORIO_COTIZACIONES
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS, hub
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.dominio.notificacion.tipos_alerta import TIPOS_ALERTA_SLA
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion


class EliminarSolicitudCotizacionUseCase:

    def __init__(
        self,
        repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion,
        repositorio_cotizaciones: RepositorioCotizaciones,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_historial: RepositorioHistorialEstadoProcesosComerciales,
        authorization_service: AuthorizationService,
        repositorio_notificaciones: RepositorioNotificaciones,
        servicio_alertas: ServicioAlertasProceso,
        servicio_archivos: ServicioArchivos
    ) -> None:
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion
        self.repositorio_cotizaciones = repositorio_cotizaciones
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.repositorio_historial = repositorio_historial
        self.authorization_service = authorization_service
        self.repositorio_notificaciones = repositorio_notificaciones
        self.servicio_alertas = servicio_alertas
        self.servicio_archivos = servicio_archivos

    def ejecutar(self, id_solicitud: int, rut_usuario: str):

        # 1. Validar que la solicitud existe

        if not self.repositorio_solicitudes_cotizacion.existe_solicitud(id_solicitud):
            raise RecursoNoEncontradoException('Solicitud no encontrada')

        # 2. Validar permisos (ELIMINAR_SOLICITUD_COTIZACION + ejecutivo comercial asignado)

        if not self.authorization_service.usuario_puede_eliminar_solicitud_cotizacion(rut_usuario, id_solicitud):
            raise UsuarioNoAutorizadoException

        # 3. Validar que el proceso comercial esté abierto

        proceso = self.repositorio_procesos_comerciales.buscar_por_solicitud_cotizacion(id_solicitud)
        if proceso is None:
            raise RecursoNoEncontradoException('Oportunidad no encontrada')
        if proceso.cerrado:
            raise ConflictoEnAccionException(
                'No se puede eliminar una solicitud de cotización de una oportunidad cerrada'
            )

        # 4. Obtener cotizaciones de la solicitud

        cotizaciones = self.repositorio_cotizaciones.obtener_por_solicitud(id_solicitud)

        # 5. Recopilar nombres de archivo para eliminación en disco

        archivos_a_eliminar = [
            c.nombre_archivo for c in cotizaciones if c.nombre_archivo is not None
        ]

        # 6. Eliminar solicitud (CASCADE elimina cotizaciones en BD)

        self.repositorio_solicitudes_cotizacion.eliminar(id_solicitud)

        # 7. Eliminar archivos del disco

        for nombre_archivo in archivos_a_eliminar:
            self.servicio_archivos.eliminar(DIRECTORIO_COTIZACIONES, nombre_archivo)

        # 8. Registrar historial + actualizar estado_actual

        ahora = datetime.now(tz=timezone.utc)

        historial = HistorialEstadoProcesoComercial(
            id_proceso_comercial=proceso.id,
            codigo_estado='SOLICITUD_COTIZACION_ELIMINADA',
            rut_registrado_por=rut_usuario,
            fecha=ahora
        )
        self.repositorio_historial.registrar(historial)

        # 9. Marcar alertas SLA del estado anterior como leídas

        destinatarios = self.servicio_alertas.marcar_leidas(
            proceso.id, TIPOS_ALERTA_SLA, ahora
        )

        if destinatarios:
            hub.publicar_desde_hilo(
                destinatarios,
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_leidas_cambio_estado'},
            )