from pydantic import BaseModel


class ParametrosDepreciacionJson(BaseModel):
    id: int | None
    antiguedad_sin_depreciacion: int
    porcentaje_por_anio: float
    antiguedad_maxima: int
    porcentaje_maximo: float
