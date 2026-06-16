from dataclasses import dataclass
from datetime import datetime


@dataclass
class SolicitudCotizacionResumen:
    id: int
    nombre_riesgo: str
    informacion_completa: bool
    ejecutivo_comercial: str
    tipo: str
    producto: str
    prioridad: str
    fecha: datetime
    cantidad_cotizaciones: int