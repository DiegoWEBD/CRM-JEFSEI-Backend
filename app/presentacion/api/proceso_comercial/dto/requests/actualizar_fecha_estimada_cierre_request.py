from datetime import date

from pydantic import BaseModel, field_validator


class ActualizarFechaEstimadaCierreRequest(BaseModel):
    fecha_estimada_cierre: str | None

    @field_validator('fecha_estimada_cierre')
    @classmethod
    def validar_formato_fecha(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        try:
            date.fromisoformat(valor)
        except ValueError:
            raise ValueError('La fecha debe tener formato YYYY-MM-DD')
        return valor
