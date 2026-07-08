from abc import ABC, abstractmethod
from app.dominio.usuario.usuario import Usuario

class RepositorioUsuarios(ABC):

    @abstractmethod
    def buscar(self, rut: str) -> Usuario | None:
        pass

    @abstractmethod
    def existe_correo(self, correo: str) -> bool:
        pass

    @abstractmethod
    def existe_telefono(self, telefono: str) -> bool:
        pass

    @abstractmethod
    def obtener_todos(self) -> list[Usuario]:
        pass

    @abstractmethod
    def registrar(self, usuario: Usuario) -> bool:
        pass

    @abstractmethod
    def actualizar(self, usuario: Usuario) -> bool:
        pass

    @abstractmethod
    def asignar_roles(self, rut: str, codigo_roles: list[str]) -> bool:
        pass

    @abstractmethod
    def eliminar(self, rut: str) -> bool:
        pass