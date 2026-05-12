from abc import ABC, abstractmethod

from app.dominio.comuna.comuna import Comuna


class RepositorioComunas(ABC):
    
    @abstractmethod
    def obtener_todas(self) -> list[Comuna]:
        pass