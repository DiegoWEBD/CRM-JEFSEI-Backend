from abc import ABC, abstractmethod

from app.aplicacion.evaluacion_proyectos.dto.estudio_comercial_condominio_resumen import EstudioComercialCondominioResumen
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio


class RepositorioEstudiosComerciales(ABC):

    @abstractmethod
    def registrar(
        self,
        estudio: EstudioComercialCondominio,
        ids_cotizacion: list[int],
        rut_usuario: str
    ) -> int:
        pass

    @abstractmethod
    def listar_por_id_solicitud_cotizacion(
        self,
        id_solicitud: int
    ) -> list[EstudioComercialCondominioResumen]:
        pass

    @abstractmethod
    def actualizar_ruta_archivo(
        self,
        id_estudio: int,
        ruta_archivo: str
    ) -> None:
        pass
