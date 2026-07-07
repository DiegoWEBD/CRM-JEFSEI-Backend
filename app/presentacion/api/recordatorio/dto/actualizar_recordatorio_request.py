from pydantic import BaseModel


class ActualizarRecordatorioRequest(BaseModel):
    titulo: str
    detalle: str | None = None
    prioridad: str
    tipo_gestion: str
    fecha_recordatorio: str
    id_prospecto: int | None = None
