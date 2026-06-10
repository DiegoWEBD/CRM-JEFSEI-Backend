from abc import ABC, abstractmethod
from app.dominio.poliza.poliza import Poliza


class RepositorioPolizas(ABC):
    
    @abstractmethod
    def registrar(self, poliza: Poliza) -> None:
        pass

    @abstractmethod
    def buscar(self, id_cliente: int) -> list[Poliza]:
        pass
