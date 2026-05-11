from abc import ABC, abstractmethod

from app.dominio.linea_negocio.linea_negocio import LineaNegocio


class RepositorioLineasNegocio(ABC):
    
    @abstractmethod
    def obtener_todas(self) -> list[LineaNegocio]:
        pass