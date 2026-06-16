from abc import ABC, abstractmethod

from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.usuario.usuario import Usuario

class RepositorioSolicitudesCotizacion(ABC):
    
    @abstractmethod
    def obtener_solicitudes_activas(self, id_prospecto: int) -> list[SolicitudCotizacion]:
        pass

    @abstractmethod
    def registrar_nueva_solicitud(self, solicitud: SolicitudCotizacion, id_prospecto: int, registrado_por: Usuario):
        pass