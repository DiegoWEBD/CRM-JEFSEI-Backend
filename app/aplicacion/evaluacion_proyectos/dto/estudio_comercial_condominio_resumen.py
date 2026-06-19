from dataclasses import dataclass
from datetime import date


@dataclass
class EstudioComercialCondominioResumen:
    id: int
    cantidad_cuotas: int
    valor_uf: float
    ruta_archivo: str | None
    fecha_emision: date | None
