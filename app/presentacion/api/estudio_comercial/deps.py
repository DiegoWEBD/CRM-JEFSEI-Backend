from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial_condominio import ArmarEstudioComercialCondominioUseCase
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.company_seguros.repositorio_company_seguros_postgres import RepositorioCompanySegurosPostgres
from app.infraestructura.cotizacion.repositorio_cotizaciones_postgres import RepositorioCotizacionesPostgres
from app.infraestructura.estudio_comercial_condominio.repositorio_estudios_comerciales_postgres import RepositorioEstudiosComercialesPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres


def get_armar_estudio_comercial_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_companies = RepositorioCompanySegurosPostgres()
    repositorio_cotizaciones = RepositorioCotizacionesPostgres()
    authorization_service = AuthorizationService(authorization_repository=AuthorizationRepositoryPostgres())

    return ArmarEstudioComercialCondominioUseCase(
        repositorio_prospectos=repositorio_prospectos,
        repositorio_company_seguros=repositorio_companies,
        repositorio_cotizaciones=repositorio_cotizaciones,
        authorization_service=authorization_service
    )


def get_repositorio_estudios():
    return RepositorioEstudiosComercialesPostgres()