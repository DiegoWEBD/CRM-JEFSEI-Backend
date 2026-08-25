from pydantic import BaseModel


class GuardarParametrosDepreciacionRequest(BaseModel):
    id: int | None = None
    antiguedad_sin_depreciacion: int
    porcentaje_por_anio: float
    antiguedad_maxima: int
    porcentaje_maximo: float
