from dataclasses import dataclass


@dataclass
class CotizacionResumen:
    id: int
    company: str
    prima_neta: float
    prima_bruta: float
    # ISO 8601; proviene del json_agg del servicio de consulta.
    fecha_vencimiento: str
    estado: str
