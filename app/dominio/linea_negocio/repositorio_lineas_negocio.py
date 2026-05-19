from abc import ABC, abstractmethod

from app.dominio.linea_negocio.linea_negocio import LineaNegocio


class RepositorioLineasNegocio(ABC):
    
    @abstractmethod
    def obtener_todas(self) -> list[LineaNegocio]:
        pass

    @abstractmethod
    def obtener_linea_negocio_de_prospecto(self, id_prospecto: int) -> LineaNegocio | None:
        pass