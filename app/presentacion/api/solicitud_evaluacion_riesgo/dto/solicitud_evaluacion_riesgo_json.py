from pydantic import BaseModel


class SolicitudEvaluacionRiesgoJson(BaseModel):
    fecha_solicitud: str
    prioridad: str
    