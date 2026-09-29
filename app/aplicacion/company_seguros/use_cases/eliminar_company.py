from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException


class EliminarCompanyUseCase:
    def __init__(self, repositorio_company_seguros: RepositorioCompanySeguros):
        self.repositorio_company_seguros = repositorio_company_seguros

    def ejecutar(self, id: int) -> None:
        company = self.repositorio_company_seguros.buscar(id)

        if company is None:
            raise RecursoNoEncontradoException("Compañía no encontrada")

        self.repositorio_company_seguros.eliminar(id)
