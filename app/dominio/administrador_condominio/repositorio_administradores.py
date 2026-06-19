from abc import ABC, abstractmethod

from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)


class RepositorioAdministradores(ABC):

    @abstractmethod
    def obtener_todos(self) -> list[AdministradorCondominio]:
        pass

    @abstractmethod
    def buscar(self, id: int) -> AdministradorCondominio | None:
        pass
