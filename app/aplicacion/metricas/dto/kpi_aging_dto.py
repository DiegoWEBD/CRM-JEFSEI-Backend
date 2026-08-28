from dataclasses import dataclass, field


@dataclass
class AgingRangoDto:
    rango: str
    cantidad: int
    porcentaje: float


@dataclass
class KpiAgingDto:
    total_abiertos: int
    rangos: list[AgingRangoDto] = field(default_factory=list)
