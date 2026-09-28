from pydantic import BaseModel, Field


class FactorCuotasCompanyJson(BaseModel):
    numero_cuotas: int
    factor: float


class CompanySegurosJson(BaseModel):
    id: int
    nombre: str
    eliminado: bool = False
    factores_cuotas: list[FactorCuotasCompanyJson] = Field(default_factory=list)
