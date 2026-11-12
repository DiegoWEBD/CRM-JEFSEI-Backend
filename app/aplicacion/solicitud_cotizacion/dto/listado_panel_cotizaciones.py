from dataclasses import dataclass

from app.aplicacion.solicitud_cotizacion.dto.contadores_panel_cotizaciones import (
    ContadoresPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.dto.fila_panel_cotizaciones import (
    FilaPanelCotizaciones,
)


@dataclass
class ListadoPanelCotizaciones:
    filas: list[FilaPanelCotizaciones]
    total: int
    contadores: ContadoresPanelCotizaciones
