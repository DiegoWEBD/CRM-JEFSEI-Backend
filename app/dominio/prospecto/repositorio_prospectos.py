from abc import ABC, abstractmethod

from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.usuario.usuario import Usuario


class RepositorioProspectos(ABC):
    
    @abstractmethod
    def registrar_prospecto_condominio(self, prospecto: ProspectoCondominio) -> int:
        pass
    
    @abstractmethod
    def buscar(self, id: int) -> Prospecto | None:
        pass

    @abstractmethod
    def buscar_prospecto_condominio(self, id: int) -> ProspectoCondominio | None:
        pass

    @abstractmethod
    def asignar_ejecutivo_comercial(self, prospecto: Prospecto, asignado_por: Usuario) -> None:
        pass

    @abstractmethod
    def asignar_ejecutivo_evaluacion_proyectos(self, prospecto: Prospecto, asignado_por: Usuario) -> None:
        pass

    @abstractmethod
    def cambiar_siguiente_estado(self, id: int) -> None:
        pass