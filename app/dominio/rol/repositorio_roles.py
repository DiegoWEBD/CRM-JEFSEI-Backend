from abc import ABC, abstractmethod

from app.dominio.rol.rol import Rol


class RepositorioRoles(ABC):

    @abstractmethod
    def obtener_todos(self) -> list[Rol]:
        pass
