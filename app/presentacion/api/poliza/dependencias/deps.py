from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.cotizacion.use_cases.registrar_renovacion_cotizada import RegistrarRenovacionCotizadaUseCase
from app.aplicacion.poliza.use_cases.obtener_poliza import ObtenerPolizaUseCase
from app.aplicacion.poliza.use_cases.obtener_polizas import ObtenerPolizasUseCase
from app.aplicacion.poliza.use_cases.registrar_poliza_a_proceso_comercial import RegistrarPolizaAProcesoComercialUseCase
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.company_seguros.repositorio_company_seguros_postgres import RepositorioCompanySegurosPostgres
from app.infraestructura.cotizacion.repositorio_cotizaciones_postgres import RepositorioCotizacionesPostgres
from app.infraestructura.poliza.repositorio_polizas_postgres import RepositorioPolizasPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres


def get_obtener_polizas_use_case():
    repositorio_polizas = RepositorioPolizasPostgres()
    repositorio_prospectos = RepositorioProspectosPostgres()
    
    return ObtenerPolizasUseCase(
        repositorio_prospectos=repositorio_prospectos,
        repositorio_polizas=repositorio_polizas
    )

def get_obtener_poliza_use_case():
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)
    repositorio_polizas = RepositorioPolizasPostgres()
    
    return ObtenerPolizaUseCase(
        authorization_service=authorization_service,
        repositorio_polizas=repositorio_polizas
    )

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

def get_registrar_poliza_a_proceso_comercial_use_case():
    authorization_repository = AuthorizationRepositoryPostgres()
    authorization_service = AuthorizationService(authorization_repository)
    repositorio_polizas = RepositorioPolizasPostgres()
    repositorio_procesos_comerciales = RepositorioProcesosComercialesPostgres()
    repositorio_companies = RepositorioCompanySegurosPostgres()


    return RegistrarPolizaAProcesoComercialUseCase(
        repositorio_polizas=repositorio_polizas,
        repositorio_companies=repositorio_companies,
        repositorio_procesos_comerciales=repositorio_procesos_comerciales,
        authorization_service=authorization_service
    )