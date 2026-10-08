from abc import ABC, abstractmethod

from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio


class RepositorioEstudiosComerciales(ABC):

    @abstractmethod
    def insertar(
        self,
        id_solicitud: int,
        nombre_archivo: str,
        rut_usuario: str,
    ) -> int:
        """Registra el estudio comercial y actualiza el estado del proceso.

        Devuelve el id del estudio registrado.
        """
        pass

    @abstractmethod
    def listar_por_id_solicitud(
        self,
        id_solicitud: int
    ) -> list[EstudioComercialCondominio]:
        pass
