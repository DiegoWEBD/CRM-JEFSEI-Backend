from abc import ABC, abstractmethod

from app.dominio.prospecto.prospecto import Prospecto


class RepositorioProspectos(ABC):
    
    @abstractmethod
    def registrar(prospecto: Prospecto) -> None:
        pass
    
    @abstractmethod
    def buscar(rut: str) -> Prospecto | None:
        pass

    @abstractmethod
    def cambiar_siguiente_estado(rut: str) -> None:
        pass

    @abstractmethod
    def obtener_todos() -> list[Prospecto]:
        pass