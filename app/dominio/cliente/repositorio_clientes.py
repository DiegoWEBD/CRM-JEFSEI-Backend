from abc import ABC, abstractmethod
from app.dominio.cliente.cliente import Cliente


class RepositorioClientes(ABC):

    @abstractmethod
    def registrar(self, cliente: Cliente) -> None:
        pass

    @abstractmethod
    def buscar(self, rut: str) -> Cliente | None:
        pass