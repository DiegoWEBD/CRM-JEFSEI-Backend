from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException


class CrearCompanyUseCase:
    def __init__(self, repositorio_company_seguros: RepositorioCompanySeguros):
        self.repositorio_company_seguros = repositorio_company_seguros

    def ejecutar(self, nombre: str) -> CompanySeguros:
        if not nombre or not nombre.strip():
            raise BadRequestException("El nombre de la compañía es obligatorio")

        nombre_limpio = nombre.strip()

        if self.repositorio_company_seguros.existe_por_nombre(nombre_limpio):
            raise RecursoYaExisteException("Ya existe una compañía con ese nombre")

        return self.repositorio_company_seguros.crear(nombre_limpio)
