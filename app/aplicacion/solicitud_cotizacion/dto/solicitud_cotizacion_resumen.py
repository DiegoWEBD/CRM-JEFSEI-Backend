from dataclasses import dataclass
from datetime import datetime


@dataclass
class SolicitudCotizacionResumen:
    id: int
    id_prospecto: int
    nombre_riesgo: str
    informacion_completa: bool
    ejecutivo_comercial: str
    tipo: str
    recotizacion: bool
    motivo_recotizacion: str | None
    producto: str
    prioridad: str
    fecha: datetime
    cantidad_cotizaciones: int
    campos_faltantes: list[str]
    estudio_disponible: bool