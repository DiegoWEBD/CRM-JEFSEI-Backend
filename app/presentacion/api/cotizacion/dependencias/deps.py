from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.cotizacion.use_cases.obtener_cotizaciones_por_solicitud import ObtenerCotizacionesPorSolicitudUseCase
from app.aplicacion.cotizacion.use_cases.registrar_cotizacion_a_solicitud import RegistrarCotizacionASolicitudUseCase
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.company_seguros.repositorio_company_seguros_postgres import RepositorioCompanySegurosPostgres
from app.infraestructura.cotizacion.repositorio_cotizaciones_postgres import RepositorioCotizacionesPostgres
from app.infraestructura.solicitud_cotizacion.repositorio_solicitudes_cotizacion_postgres import RepositorioSolicitudesCotizacionPostgres


def get_obtener_cotizaciones_por_solicitud_use_case():
    repositorio_solicitudes_cotizacion = RepositorioSolicitudesCotizacionPostgres()
    repositorio_cotizaciones = RepositorioCotizacionesPostgres()
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)

    return ObtenerCotizacionesPorSolicitudUseCase(
        repositorio_cotizaciones=repositorio_cotizaciones,
        authorization_service=authorization_service,
        repositorio_solicitudes_cotizacion=repositorio_solicitudes_cotizacion
    )

def get_registrar_cotizacion_a_solicitud_use_case():
    repositorio_companies = RepositorioCompanySegurosPostgres()
    repositorio_solicitudes_cotizacion = RepositorioSolicitudesCotizacionPostgres()
    repositorio_cotizaciones = RepositorioCotizacionesPostgres()
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)

    return RegistrarCotizacionASolicitudUseCase(
        repositorio_cotizaciones=repositorio_cotizaciones,
        authorization_service=authorization_service,
        repositorio_solicitudes_cotizacion=repositorio_solicitudes_cotizacion,
        repositorio_companies=repositorio_companies
    )