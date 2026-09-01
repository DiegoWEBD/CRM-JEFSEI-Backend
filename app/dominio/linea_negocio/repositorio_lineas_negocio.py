from abc import ABC, abstractmethod

from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.producto.producto import Producto


class RepositorioLineasNegocio(ABC):
    
    @abstractmethod
    def obtener_todas(self) -> list[LineaNegocio]:
        pass

    @abstractmethod
    def obtener_linea_negocio_de_prospecto(self, id_prospecto: int) -> LineaNegocio | None:
        pass

    @abstractmethod
    def obtener_por_id(self, id: int) -> LineaNegocio | None:
        pass

    @abstractmethod
    def obtener_productos_por_linea_negocio(self, id_linea_negocio: int) -> list[Producto]:
        pass