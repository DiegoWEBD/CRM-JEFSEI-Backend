from pydantic import BaseModel


class CrearPlanPagoRequest(BaseModel):
    numero_cuotas: int
    fecha_primera_cuota: str