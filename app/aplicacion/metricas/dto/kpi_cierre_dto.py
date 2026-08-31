from dataclasses import dataclass


@dataclass
class KpiCierreDto:
    total_procesos_cerrados: int
    procesos_ganados: int
    procesos_perdidos: int
    tasa_cierre_pct: float
    tasa_perdida_pct: float
