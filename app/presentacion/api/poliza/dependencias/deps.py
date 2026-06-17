from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.cotizacion.use_cases.registrar_renovacion_cotizada import RegistrarRenovacionCotizadaUseCase
from app.aplicacion.poliza.use_cases.obtener_polizas import ObtenerPolizasUseCase
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.cotizacion.repositorio_cotizaciones_postgres import RepositorioCotizacionesPostgres
from app.infraestructura.poliza.repositorio_polizas_postgres import RepositorioPolizasPostgres


def get_obtener_polizas_use_case():
    repositorio_polizas = RepositorioPolizasPostgres()
    return ObtenerPolizasUseCase(repositorio_polizas)

def get_registrar_renovacion_cotizada_use_case():
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)
    repositorio_polizas = RepositorioPolizasPostgres()
    repositorio_cotizaciones = RepositorioCotizacionesPostgres()

    return RegistrarRenovacionCotizadaUseCase(
        authorization_service=authorization_service,
        repositorio_cotizaciones=repositorio_cotizaciones,
        repositorio_polizas=repositorio_polizas
    )