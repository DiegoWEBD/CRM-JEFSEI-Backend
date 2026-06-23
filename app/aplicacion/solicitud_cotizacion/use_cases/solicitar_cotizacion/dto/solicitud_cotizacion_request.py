from typing import Optional

from pydantic import BaseModel


class SolicitudCotizacionRequest(BaseModel):
    prioridad: str 
    observaciones: str | None
    tipo: str
    motivo_recotizacion: Optional[str] = None
    id_solicitud_previa: int | None