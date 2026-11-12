from abc import ABC, abstractmethod

from app.aplicacion.solicitud_cotizacion.dto.contadores_solicitudes_cotizacion import (
    ContadoresSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.filtro_solicitudes_cotizacion import (
    FiltroSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import (
    SolicitudCotizacionResumen,
)


class ConsultaSolicitudesCotizacionService(ABC):

    @abstractmethod
    def listar(
        self,
        rut_scoping: str | None,
        filtro: FiltroSolicitudesCotizacion,
    ) -> tuple[list[SolicitudCotizacionResumen], int]:
        pass

    @abstractmethod
    def contadores(self, rut_scoping: str | None) -> ContadoresSolicitudesCotizacion:
        pass
