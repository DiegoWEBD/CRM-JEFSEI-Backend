from dataclasses import dataclass
from datetime import datetime

from app.aplicacion.solicitud_cotizacion.dto.cotizacion_resumen import CotizacionResumen


@dataclass
class FilaPanelCotizaciones:
    id: int
    id_prospecto: int
    id_proceso_comercial: int
    cliente: str
    linea_seguro: str
    ejecutivo_comercial: str
    prioridad: str
    fecha: datetime
    cantidad_cotizaciones: int
    vencimiento_mas_proximo: datetime | None
    estado: str | None
    tiene_estudio: bool
    id_estudio: int | None
    cotizaciones: list[CotizacionResumen]
