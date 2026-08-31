from dataclasses import dataclass


@dataclass
class KpiRenovacionDto:
    polizas_vencidas: int
    polizas_renovadas: int
    tasa_renovacion_pct: float
