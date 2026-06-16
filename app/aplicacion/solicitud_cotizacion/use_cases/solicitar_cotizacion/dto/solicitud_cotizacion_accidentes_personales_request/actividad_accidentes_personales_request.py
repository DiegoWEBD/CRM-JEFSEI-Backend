from dataclasses import dataclass


@dataclass
class ActividadAccidentesPersonalesRequest:
    actividad: str
    numero_asegurados: int