from dataclasses import dataclass


@dataclass
class KpiTiempoCierreDto:
    procesos_cerrados: int
    tiempo_promedio_dias: float
    tiempo_minimo_dias: float
    tiempo_maximo_dias: float
