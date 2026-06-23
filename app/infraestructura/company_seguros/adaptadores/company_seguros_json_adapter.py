from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.presentacion.api.company_seguros.dto.company_seguros_json import CompanySegurosJson


class CompanySegurosJsonAdapter:

    def __init__(self, company: CompanySeguros) -> None:
        self.company = company

    def to_json(self) -> CompanySegurosJson:
        return CompanySegurosJson(
            id=self.company.id,
            nombre=self.company.nombre
        )