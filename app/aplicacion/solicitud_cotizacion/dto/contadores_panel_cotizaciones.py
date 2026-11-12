from dataclasses import dataclass


@dataclass
class ContadoresPanelCotizaciones:
    cotizaciones_vigentes: int
    cotizaciones_por_vencer: int
    cotizaciones_vencidas: int
    estudios_pendientes: int
    estudios_emitidos: int
