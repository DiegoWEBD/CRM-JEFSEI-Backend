from abc import ABC, abstractmethod

from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio


class RepositorioProspectos(ABC):
    
    @abstractmethod
    def registrar_prospecto_condominio(prospecto: ProspectoCondominio) -> None:
        pass
    
    @abstractmethod
    def buscar(id: int) -> Prospecto | None:
        pass

    @abstractmethod
    def cambiar_siguiente_estado(id: int) -> None:
        pass