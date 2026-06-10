from datetime import datetime

from pydantic import BaseModel


class HistorialEstadoJson(BaseModel):
    estado_anterior: str | None
    estado_actual: str
    fecha_registro: datetime
    dias_limite: int | None
    dias_transcurridos: int
    proxima_accion: str | None
    motivo_cambio: str | None
    cambiado_por: str