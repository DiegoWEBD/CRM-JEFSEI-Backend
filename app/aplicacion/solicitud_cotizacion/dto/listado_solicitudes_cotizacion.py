from dataclasses import dataclass

from app.aplicacion.solicitud_cotizacion.dto.contadores_solicitudes_cotizacion import (
    ContadoresSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import (
    SolicitudCotizacionResumen,
)


@dataclass
class ListadoSolicitudesCotizacion:
    solicitudes: list[SolicitudCotizacionResumen]
    total: int
    contadores: ContadoresSolicitudesCotizacion
