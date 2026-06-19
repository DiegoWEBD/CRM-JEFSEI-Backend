from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros


class ObtenerTodasLasCompaniesSegurosUseCase:

    def __init__(self, repositorio_company_seguros: RepositorioCompanySeguros):
        self.repositorio_company_seguros = repositorio_company_seguros

    def ejecutar(self) -> list[CompanySeguros]:
        return self.repositorio_company_seguros.obtener_todas()
