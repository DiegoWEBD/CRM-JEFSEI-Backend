from dataclasses import dataclass


@dataclass
class KpiPrimaMetaEjecutivoDto:
    rut_ejecutivo: str
    nombre_ejecutivo: str
    prima_neta_uf: float
    meta_mensual_uf: float | None
    cumplimiento_pct: float
    diferencia_uf: float


@dataclass
class KpiPrimaMetaResumenDto:
    prima_neta_uf: float
    meta_uf: float
    cumplimiento_pct: float
