from dataclasses import dataclass

ESTADOS_PANEL_COTIZACIONES = (
    'cotizaciones_vigentes',
    'cotizaciones_por_vencer',
    'cotizaciones_vencidas',
    'estudios_pendientes',
    'estudios_emitidos',
)

PRIORIDADES_PANEL_COTIZACIONES = ('normal', 'alta')


@dataclass
class FiltroPanelCotizaciones:
    texto_busqueda: str | None = None
    estado: str | None = None
    prioridad: str | None = None
    rut_ejecutivo: str | None = None
    pagina: int = 1
    tamano_pagina: int = 10
