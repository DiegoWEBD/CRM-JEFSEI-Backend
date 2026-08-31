from dataclasses import dataclass


@dataclass
class KpiConversionDto:
    total_prospectos: int
    prospectos_convertidos: int
    tasa_conversion_pct: float
