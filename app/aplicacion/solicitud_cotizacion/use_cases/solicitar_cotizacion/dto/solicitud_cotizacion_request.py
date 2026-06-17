from typing import Optional

from pydantic import BaseModel


class SolicitudCotizacionRequest(BaseModel):
    id_prospecto: int
    prioridad: str 
    observaciones: str | None
    tipo: str
    motivo_recotizacion: Optional[str] = None
    id_solicitud_previa: int | None