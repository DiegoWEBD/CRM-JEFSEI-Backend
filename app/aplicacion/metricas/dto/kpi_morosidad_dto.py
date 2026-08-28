from dataclasses import dataclass


@dataclass
class KpiMorosidadDto:
    total_cuotas: int
    cuotas_vencidas: int
    cuotas_morosas: int
    tasa_morosidad_pct: float
