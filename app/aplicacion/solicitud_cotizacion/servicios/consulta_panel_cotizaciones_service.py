from abc import ABC, abstractmethod

from app.aplicacion.solicitud_cotizacion.dto.contadores_panel_cotizaciones import (
    ContadoresPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.dto.filtro_panel_cotizaciones import (
    FiltroPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.dto.fila_panel_cotizaciones import (
    FilaPanelCotizaciones,
)


class ConsultaPanelCotizacionesService(ABC):

    @abstractmethod
    def listar(
        self,
        rut_scoping: str | None,
        filtro: FiltroPanelCotizaciones,
    ) -> tuple[list[FilaPanelCotizaciones], int]:
        pass

    @abstractmethod
    def contadores(self, rut_scoping: str | None) -> ContadoresPanelCotizaciones:
        pass
