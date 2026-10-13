from pydantic import BaseModel


class ActualizarEstadoConfiguracionRequest(BaseModel):
    # 0..1
    probabilidad_cierre: float
