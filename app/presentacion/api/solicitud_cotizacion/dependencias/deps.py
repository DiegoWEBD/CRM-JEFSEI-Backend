from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.obtener_procesos_comerciales import ObtenerProcesosComercialesUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_detalle_solicitud import ObtenerDetalleSolicitudUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_resumen_solicitudes_cotizacion_activas import ObtenerResumenSolicitudesCotizacionActivasUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.obtener_solicitudes_cotizacion import ObtenerSolicitudesCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_cotizacion import SolicitarCotizacionUseCase
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.solicitar_recotizacion import SolicitarRecotizacionUseCase
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.solicitud_cotizacion.repositorio_solicitudes_cotizacion_postgres import RepositorioSolicitudesCotizacionPostgres
from app.infraestructura.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_postgres_service import ConsultaSolicitudesCotizacionPostgresService


def get_obtener_solicitudes_cotizacion_use_case():
    repositorio_solicitudes = RepositorioSolicitudesCotizacionPostgres()
    repositorio_procesos = RepositorioProcesosComercialesPostgres()

    return ObtenerSolicitudesCotizacionUseCase(
        repositorio_solicitudes=repositorio_solicitudes,
        repositorio_procesos_comerciales=repositorio_procesos
    )

def get_obtener_procesos_comerciales_use_case():
    repositorio = RepositorioProcesosComercialesPostgres()
    repositorio_prospectos = RepositorioProspectosPostgres()
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)

    return ObtenerProcesosComercialesUseCase(
        authorization_service=authorization_service,
        repositorio_procesos_comerciales=repositorio,
        repositorio_prospectos=repositorio_prospectos
    )

def get_consulta_solicitudes_cotizacion_service():
    return ConsultaSolicitudesCotizacionPostgresService()

def get_solicitar_cotizacion_use_case():
    repositorio = RepositorioSolicitudesCotizacionPostgres()
    repositorio_procesos_comerciales = RepositorioProcesosComercialesPostgres()
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)

    return SolicitarCotizacionUseCase(
        repositorio_solicitudes_cotizacion=repositorio,
        repositorio_procesos_comerciales=repositorio_procesos_comerciales,
        authorization_service=authorization_service
    )

def get_solicitar_recotizacion_use_case():
    repositorio = RepositorioSolicitudesCotizacionPostgres()
    repositorio_procesos_comerciales = RepositorioProcesosComercialesPostgres()
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)

    return SolicitarRecotizacionUseCase(
        repositorio_solicitudes_cotizacion=repositorio,
        repositorio_procesos_comerciales=repositorio_procesos_comerciales,
        authorization_service=authorization_service
    )

def get_obtener_resumen_solicitudes_cotizacion_activas_use_case():
    service = ConsultaSolicitudesCotizacionPostgresService()
    repositorio = RepositorioProspectosPostgres()

    return ObtenerResumenSolicitudesCotizacionActivasUseCase(service, repositorio)

def get_obtener_detalle_solicitud_use_case():
    repositorio = RepositorioSolicitudesCotizacionPostgres()

    return ObtenerDetalleSolicitudUseCase(repositorio)