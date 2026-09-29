from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.presentacion.api.company_seguros.dto.company_seguros_json import (
    CompanySegurosJson,
    FactorCuotasCompanyJson,
)


class CompanySegurosJsonAdapter:

    def __init__(self, company: CompanySeguros) -> None:
        self.company = company

    def to_json(self) -> CompanySegurosJson:
        return CompanySegurosJson(
            id=self.company.id,
            nombre=self.company.nombre,
            eliminado=self.company.eliminado,
            factores_cuotas=[
                FactorCuotasCompanyJson(
                    numero_cuotas=factor.numero_cuotas,
                    factor=factor.factor,
                )
                for factor in self.company.factores_cuotas
            ],
        )
