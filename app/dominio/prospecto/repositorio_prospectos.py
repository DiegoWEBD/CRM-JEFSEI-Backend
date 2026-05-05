from abc import ABC, abstractmethod

from app.dominio.prospecto.prospecto import Prospecto


class RepositorioProspectos(ABC):
    
    @abstractmethod
    def registrar(prospecto: Prospecto) -> None:
        pass
    
    @abstractmethod
    def buscar(id: int) -> Prospecto | None:
        pass

    @abstractmethod
    def cambiar_siguiente_estado(id: int) -> None:
        pass