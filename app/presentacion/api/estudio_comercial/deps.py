from app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial_condominio import ArmarEstudioComercialCondominioUseCase
from app.infraestructura.company_seguros.repositorio_company_seguros_postgres import RepositorioCompanySegurosPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres


def get_armar_estudio_comercial_use_case():
    repositorio_prospectos = RepositorioProspectosPostgres()
    repositorio_companies = RepositorioCompanySegurosPostgres()

    return ArmarEstudioComercialCondominioUseCase(
        repositorio_prospectos=repositorio_prospectos,
        repositorio_company_seguros=repositorio_companies
    )