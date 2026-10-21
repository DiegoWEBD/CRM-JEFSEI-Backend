from app.aplicacion.authorization.authorization_service_factory import AuthorizationServiceFactory
from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.proceso_comercial.use_cases.obtener_procesos_comerciales import ObtenerProcesosComercialesUseCase
from app.aplicacion.proyeccion.servicios.servicio_proyecciones_comerciales import ServicioProyeccionesComerciales
from app.aplicacion.solicitud_cotizacion.use_cases.eliminar_solicitud_cotizacion import EliminarSolicitudCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_detalle_solicitud import ObtenerDetalleSolicitudUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_resumen_solicitudes_cotizacion_activas import ObtenerResumenSolicitudesCotizacionActivasUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_solicitudes_cotizacion import ObtenerSolicitudesCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion import SolicitarCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_recotizacion import SolicitarRecotizacionUseCase
from app.aplicacion.archivo.servicios.servicio_archivos import ServicioArchivos
from app.infraestructura.cotizacion.repositorio_cotizaciones_postgres import RepositorioCotizacionesPostgres
from app.infraestructura.historial_estado.repositorio_historial_estado_procesos_comerciales_postgres import RepositorioHistorialEstadoProcesosComercialesPostgres
from app.infraestructura.notificacion.repositorio_notificaciones_postgres import RepositorioNotificacionesPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.solicitud_cotizacion.repositorio_solicitudes_cotizacion_postgres import RepositorioSolicitudesCotizacionPostgres
from app.infraestructura.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_postgres_service import ConsultaSolicitudesCotizacionPostgresService


def get_obtener_solicitudes_cotizacion_use_case():
    repositorio_solicitudes = RepositorioSolicitudesCotizacionPostgres()
    repositorio_procesos = RepositorioProcesosComercialesPostgres()

    return ObtenerSolicitudesCotizacionUseCase(
        repositorio_solicitudes=repositorio_solicitudes,
        repositorio_procesos_comerciales=repositorio_procesos,
        authorization_service=AuthorizationServiceFactory.crear_authorization_service()
    )

def get_obtener_procesos_comerciales_use_case():
    repositorio = RepositorioProcesosComercialesPostgres()
    repositorio_prospectos = RepositorioProspectosPostgres()
    authorization_service = AuthorizationServiceFactory.crear_authorization_service()

    servicio_proyecciones_comerciales = ServicioProyeccionesComerciales(
        repositorio_solicitudes_cotizacion=RepositorioSolicitudesCotizacionPostgres(),
        repositorio_cotizaciones=RepositorioCotizacionesPostgres()
    )

    return ObtenerProcesosComercialesUseCase(
        authorization_service=authorization_service,
        repositorio_procesos_comerciales=repositorio,
        repositorio_prospectos=repositorio_prospectos,
        servicio_proyecciones_comerciales=servicio_proyecciones_comerciales
    )

def get_consulta_solicitudes_cotizacion_service():
    return ConsultaSolicitudesCotizacionPostgresService()

def get_authorization_service():
    return AuthorizationServiceFactory.crear_authorization_service()

def get_solicitar_cotizacion_use_case():
    repositorio = RepositorioSolicitudesCotizacionPostgres()
    repositorio_procesos_comerciales = RepositorioProcesosComercialesPostgres()
    authorization_service = AuthorizationServiceFactory.crear_authorization_service()
    repositorio_notificaciones = RepositorioNotificacionesPostgres()

    return SolicitarCotizacionUseCase(
        repositorio_solicitudes_cotizacion=repositorio,
        repositorio_procesos_comerciales=repositorio_procesos_comerciales,
        authorization_service=authorization_service,
        repositorio_notificaciones=repositorio_notificaciones,
        servicio_alertas=ServicioAlertasProceso(repositorio_notificaciones)
    )

def get_solicitar_recotizacion_use_case():
    repositorio = RepositorioSolicitudesCotizacionPostgres()
    repositorio_procesos_comerciales = RepositorioProcesosComercialesPostgres()
    authorization_service = AuthorizationServiceFactory.crear_authorization_service()
    repositorio_notificaciones = RepositorioNotificacionesPostgres()

    return SolicitarRecotizacionUseCase(
        repositorio_solicitudes_cotizacion=repositorio,
        repositorio_procesos_comerciales=repositorio_procesos_comerciales,
        authorization_service=authorization_service,
        repositorio_notificaciones=repositorio_notificaciones,
        servicio_alertas=ServicioAlertasProceso(repositorio_notificaciones)
    )

def get_obtener_resumen_solicitudes_cotizacion_activas_use_case():
    service = ConsultaSolicitudesCotizacionPostgresService()
    repositorio = RepositorioProspectosPostgres()

    return ObtenerResumenSolicitudesCotizacionActivasUseCase(service, repositorio)

def get_obtener_detalle_solicitud_use_case():
    repositorio = RepositorioSolicitudesCotizacionPostgres()
    return ObtenerDetalleSolicitudUseCase(
        repositorio,
        AuthorizationServiceFactory.crear_authorization_service()
    )


def get_eliminar_solicitud_cotizacion_use_case():
    repositorio_notificaciones = RepositorioNotificacionesPostgres()

    return EliminarSolicitudCotizacionUseCase(
        repositorio_solicitudes_cotizacion=RepositorioSolicitudesCotizacionPostgres(),
        repositorio_cotizaciones=RepositorioCotizacionesPostgres(),
        repositorio_procesos_comerciales=RepositorioProcesosComercialesPostgres(),
        repositorio_historial=RepositorioHistorialEstadoProcesosComercialesPostgres(),
        authorization_service=AuthorizationServiceFactory.crear_authorization_service(),
        repositorio_notificaciones=repositorio_notificaciones,
        servicio_alertas=ServicioAlertasProceso(repositorio_notificaciones),
        servicio_archivos=ServicioArchivos()
    )

