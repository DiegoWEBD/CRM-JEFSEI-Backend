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
    def obtener_paginadas(
        self,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 15,
    ) -> tuple[list[CompanySeguros], int]:
        pass

    @abstractmethod
    def obtener_factores_cuotas(self, id_company: int) -> list[FactorCuotasCompany]:
        pass

    @abstractmethod
    def existe_por_nombre(self, nombre: str, id_excluir: int | None = None) -> bool:
        pass

    @abstractmethod
    def crear(self, nombre: str) -> CompanySeguros:
        pass

    @abstractmethod
    def actualizar_nombre(self, id: int, nombre: str) -> None:
        pass

    @abstractmethod
    def eliminar(self, id: int) -> None:
        pass

    @abstractmethod
    def reemplazar_factores_cuotas(
        self, id_company: int, factores: list[tuple[int, float]]
    ) -> None:
        pass
