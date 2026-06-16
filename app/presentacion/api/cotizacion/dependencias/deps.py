from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.cotizacion.use_cases.obtener_cotizaciones_por_solicitud import ObtenerCotizacionesPorSolicitudUseCase
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.cotizacion.repositorio_cotizaciones_postgres import RepositorioCotizacionesPostgres
from app.infraestructura.solicitud_cotizacion.repositorio_solicitudes_cotizacion_postgres import RepositorioSolicitudesCotizacionPostgres


def get_obtener_cotizaciones_por_solicitud():
    repositorio_solicitudes_cotizacion = RepositorioSolicitudesCotizacionPostgres()
    repositorio_cotizaciones = RepositorioCotizacionesPostgres()
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)

    return ObtenerCotizacionesPorSolicitudUseCase(
        repositorio_cotizaciones=repositorio_cotizaciones,
        authorization_service=authorization_service,
        repositorio_solicitudes_cotizacion=repositorio_solicitudes_cotizacion
    )