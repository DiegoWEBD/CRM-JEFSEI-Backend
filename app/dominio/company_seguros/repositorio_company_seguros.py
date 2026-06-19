from abc import ABC, abstractmethod

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany


class RepositorioCompanySeguros(ABC):

    @abstractmethod
    def buscar(self, id: int) -> CompanySeguros | None:
        pass

    @abstractmethod
    def obtener_todas(self) -> list[CompanySeguros]:
        pass

    @abstractmethod
    def obtener_factores_cuotas(self, id_company: int) -> list[FactorCuotasCompany]:
        pass