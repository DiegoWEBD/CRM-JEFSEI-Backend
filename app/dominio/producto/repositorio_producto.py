from abc import ABC, abstractmethod
from app.dominio.producto.producto import Producto


class RepositorioProducto(ABC):

    @abstractmethod
    def obtener_activos(
        self,
        id_linea_negocio: int | None = None,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 20,
    ) -> tuple[list[Producto], int]:
        pass

    @abstractmethod
    def obtener_por_id(self, id: int) -> Producto | None:
        pass

    @abstractmethod
    def crear(self, producto: Producto) -> bool:
        pass

    @abstractmethod
    def actualizar(self, producto: Producto) -> bool:
        pass

    @abstractmethod
    def eliminar(self, id: int) -> bool:
        pass
