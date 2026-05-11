from datetime import datetime

from pydantic import BaseModel


class HistorialEstadoJson(BaseModel):
    estado: str
    fecha_registro: datetime
    dias_limite: int
    dias_transcurridos: int
    siguiente_estado: str | None