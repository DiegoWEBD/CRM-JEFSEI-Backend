from abc import ABC, abstractmethod

from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.usuario.usuario import Usuario

class RepositorioSolicitudesCotizacion(ABC):
    
    @abstractmethod
    def buscar(self, id: int) -> SolicitudCotizacion | None:
        pass

    @abstractmethod
    def obtener_solicitudes(self, id_proceso_comercial: int) -> list[SolicitudCotizacion]:
        pass

    @abstractmethod
    def nueva_solicitud(self, solicitud: SolicitudCotizacion, id_proceso_comercial: int, registrado_por: Usuario):
        pass

    @abstractmethod
    def registrar_solicitud_recotizacion(self, solicitud: SolicitudCotizacion, id_proceso_comercial: int, registrado_por: Usuario):
        pass

    @abstractmethod
    def existe_solicitud(self, id) -> bool:
        pass