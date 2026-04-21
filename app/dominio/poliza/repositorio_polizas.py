from abc import ABC, abstractmethod
from app.dominio.poliza.poliza import Poliza


class RepositorioPolizas(ABC):
    
    @abstractmethod
    def registrar(poliza: Poliza) -> None:
        pass

    @abstractmethod
    def buscar(rut: str) -> Poliza | None:
        pass
