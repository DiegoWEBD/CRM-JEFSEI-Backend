from abc import ABC, abstractmethod

from app.dominio.sucursal.sucursal import Sucursal


class RepositorioSucursales(ABC):
    
    @abstractmethod
    def obtener_sucursales(self) -> list[Sucursal]:
        pass