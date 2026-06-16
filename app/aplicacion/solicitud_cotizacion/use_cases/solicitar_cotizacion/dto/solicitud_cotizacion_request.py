from pydantic import BaseModel


class SolicitudCotizacionRequest(BaseModel):
    id_prospecto: int
    prioridad: str 
    observaciones: str | None
    tipo: str
    recotizacion: bool
    id_solicitud_previa: int | None