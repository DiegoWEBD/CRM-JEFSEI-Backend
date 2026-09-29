from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import ActualizarFactoresCuotasUseCase
from app.aplicacion.company_seguros.use_cases.actualizar_nombre_company import ActualizarNombreCompanyUseCase
from app.aplicacion.company_seguros.use_cases.crear_company import CrearCompanyUseCase
from app.aplicacion.company_seguros.use_cases.eliminar_company import EliminarCompanyUseCase
from app.aplicacion.company_seguros.use_cases.obtener_companies_paginadas import ObtenerCompaniesSegurosPaginadasUseCase
from app.infraestructura.company_seguros.repositorio_company_seguros_postgres import RepositorioCompanySegurosPostgres


def get_obtener_companies_seguros_paginadas_use_case():
    repositorio = RepositorioCompanySegurosPostgres()
    return ObtenerCompaniesSegurosPaginadasUseCase(repositorio)


def get_crear_company_use_case():
    repositorio = RepositorioCompanySegurosPostgres()
    return CrearCompanyUseCase(repositorio)


def get_actualizar_nombre_company_use_case():
    repositorio = RepositorioCompanySegurosPostgres()
    return ActualizarNombreCompanyUseCase(repositorio)


def get_eliminar_company_use_case():
    repositorio = RepositorioCompanySegurosPostgres()
    return EliminarCompanyUseCase(repositorio)


def get_actualizar_factores_cuotas_use_case():
    repositorio = RepositorioCompanySegurosPostgres()
    return ActualizarFactoresCuotasUseCase(repositorio)
