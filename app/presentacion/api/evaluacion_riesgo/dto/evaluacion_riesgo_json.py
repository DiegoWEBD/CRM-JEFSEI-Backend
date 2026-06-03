from pydantic import BaseModel


class EvaluacionRiesgoJson(BaseModel):
    uf_por_metro_cuadrado: float | None
    porcentaje_depreciacion: float | None
    porcentaje_espacios_comunes: float | None
    observaciones: str | None  