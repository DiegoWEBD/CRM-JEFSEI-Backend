from abc import ABC, abstractmethod

from app.dominio.company_seguros.company_seguros import CompanySeguros


class RepositorioCompanySeguros(ABC):

    @abstractmethod
    def buscar(self, id: int) -> CompanySeguros | None:
        pass