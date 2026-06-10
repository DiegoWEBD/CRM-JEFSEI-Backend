from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProcesoComercialResumen:
    id: int
    codigo_estado: str
    nombre_estado: str
    fecha_ultima_accion: datetime