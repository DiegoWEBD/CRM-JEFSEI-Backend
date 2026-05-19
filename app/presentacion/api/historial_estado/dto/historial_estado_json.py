from datetime import datetime

from pydantic import BaseModel


class HistorialEstadoJson(BaseModel):
    estado_anterior: str | None
    estado_actual: str
    color: str
    fecha_registro: datetime
    dias_limite: int
    dias_transcurridos: int
    proxima_accion: str | None
    motivo_cambio: str | None
    cambiado_por: str