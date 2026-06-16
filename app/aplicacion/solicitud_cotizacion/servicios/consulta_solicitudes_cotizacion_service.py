from abc import ABC, abstractmethod

from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import SolicitudCotizacionResumen


class ConsultaSolicitudesCotizacionService(ABC):

    @abstractmethod
    def obtener_todas(self, rut_usuario: str | None) -> list[SolicitudCotizacionResumen]:
        pass