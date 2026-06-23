from pydantic import BaseModel


class HistorialEstadoResumen(BaseModel):
    estado: str
    observacion: str | None
    registrado_por: str
    fecha_registro: str