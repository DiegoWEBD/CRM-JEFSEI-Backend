from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.company_seguros.repositorio_company_seguros import RepositorioCompanySeguros


class ObtenerCompaniesSegurosPaginadasUseCase:

    def __init__(self, repositorio_company_seguros: RepositorioCompanySeguros):
        self.repositorio_company_seguros = repositorio_company_seguros

    def ejecutar(
        self,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 15,
    ) -> tuple[list[CompanySeguros], int]:
        return self.repositorio_company_seguros.obtener_paginadas(
            texto_busqueda=texto_busqueda,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )
