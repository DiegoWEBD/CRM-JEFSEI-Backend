from abc import ABC, abstractmethod

from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio


class RepositorioEstudiosComerciales(ABC):

    @abstractmethod
    def insertar(
        self,
        id_solicitud: int,
        nombre_archivo: str
    ) -> int:
        pass

    @abstractmethod
    def listar_por_id_solicitud(
        self,
        id_solicitud: int
    ) -> list[EstudioComercialCondominio]:
        pass
