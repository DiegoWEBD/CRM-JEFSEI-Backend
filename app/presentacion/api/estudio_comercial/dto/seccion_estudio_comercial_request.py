from pydantic import BaseModel


class SeccionEstudioComercialRequest(BaseModel):
    titulo: str
    monto_asegurado: float
    numero_propietarios: int | None