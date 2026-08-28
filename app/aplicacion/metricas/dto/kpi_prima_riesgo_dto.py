from dataclasses import dataclass


@dataclass
class KpiPrimaRiesgoDto:
    prima_en_riesgo_uf: float
    polizas_en_riesgo: int
