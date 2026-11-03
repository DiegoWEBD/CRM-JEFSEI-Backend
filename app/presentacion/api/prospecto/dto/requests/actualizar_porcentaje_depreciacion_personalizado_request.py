from pydantic import BaseModel, Field


class ActualizarPorcentajeDepreciacionPersonalizadoRequest(BaseModel):
    porcentaje_depreciacion_personalizado: float | None = Field(None, ge=0, le=1)
