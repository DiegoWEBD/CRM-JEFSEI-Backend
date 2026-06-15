
from dataclasses import dataclass

from app.dominio.poliza.poliza import Poliza


@dataclass
class PolizasPorProducto:
    producto: str
    polizas: list[Poliza]