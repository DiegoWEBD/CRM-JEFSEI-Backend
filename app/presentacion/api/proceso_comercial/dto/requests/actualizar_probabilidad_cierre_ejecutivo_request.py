from pydantic import BaseModel, field_validator


class ActualizarProbabilidadCierreEjecutivoRequest(BaseModel):
    probabilidad_cierre_ejecutivo: float | None

    @field_validator('probabilidad_cierre_ejecutivo')
    @classmethod
    def validar_rango_probabilidad(cls, valor: float | None) -> float | None:
        if valor is None:
            return valor
        if not 0 <= valor <= 1:
            raise ValueError('La probabilidad de cierre debe estar entre 0 y 1')
        return valor
