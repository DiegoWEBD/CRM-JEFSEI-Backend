from pydantic import BaseModel


class ActualizarEstadoConfiguracionRequest(BaseModel):
    dias_limite: int | None
    probabilidad_cierre: float
