from pydantic import BaseModel, Field


class FactorCuotasRequest(BaseModel):
    numero_cuotas: int
    factor: float


class ActualizarFactoresCuotasRequest(BaseModel):
    factores: list[FactorCuotasRequest] = Field(default_factory=list)
