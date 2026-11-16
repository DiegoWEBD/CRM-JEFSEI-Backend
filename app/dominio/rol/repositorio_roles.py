from abc import ABC, abstractmethod

from app.dominio.rol.rol import Rol


class RepositorioRoles(ABC):

    @abstractmethod
    def obtener_todos(self) -> list[Rol]:
        pass

    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> Rol | None:
        pass

    @abstractmethod
    def obtener_con_permisos(self) -> list[Rol]:
        pass

    @abstractmethod
    def asignar_permisos(self, codigo_rol: str, codigos_permiso: list[str]) -> bool:
        pass
