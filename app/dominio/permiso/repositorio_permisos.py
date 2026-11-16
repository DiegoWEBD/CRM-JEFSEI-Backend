from abc import ABC, abstractmethod

from app.dominio.permiso.permiso import Permiso


class RepositorioPermisos(ABC):

    @abstractmethod
    def obtener_todos(self) -> list[Permiso]:
        pass

    @abstractmethod
    def obtener_por_codigos(self, codigos: list[str]) -> list[Permiso]:
        pass
