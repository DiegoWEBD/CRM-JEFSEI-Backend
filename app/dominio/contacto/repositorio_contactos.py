from abc import ABC, abstractmethod

from app.dominio.contacto.contacto import Contacto


class RepositorioContactos(ABC):

    @abstractmethod
    def obtener_por_prospecto(self, id_prospecto: int) -> list[Contacto]:
        pass

    @abstractmethod
    def buscar(self, id: int) -> Contacto | None:
        pass

    @abstractmethod
    def guardar(self, contacto: Contacto) -> Contacto:
        pass

    @abstractmethod
    def actualizar(self, contacto: Contacto) -> Contacto:
        pass

    @abstractmethod
    def eliminar(self, id: int) -> bool:
        pass