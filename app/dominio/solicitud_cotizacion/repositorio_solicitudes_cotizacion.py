from abc import ABC, abstractmethod

from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion


class RepositorioSolicitudesCotizacion(ABC):
    
    @abstractmethod
    def obtener_solicitudes_activas(self, id_prospecto: int) -> list[SolicitudCotizacion]:
        pass