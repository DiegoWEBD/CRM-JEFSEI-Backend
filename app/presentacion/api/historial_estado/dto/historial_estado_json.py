from datetime import datetime

from pydantic import BaseModel


class HistorialEstadoJson(BaseModel):
    estado: str
    color: str
    fecha_registro: datetime
    dias_limite: int
    dias_transcurridos: int
    proxima_accion: str | None