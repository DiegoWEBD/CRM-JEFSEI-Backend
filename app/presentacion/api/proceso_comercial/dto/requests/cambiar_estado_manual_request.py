from pydantic import BaseModel


class CambiarEstadoManualRequest(BaseModel):
    codigo_estado_destino: str
    observacion: str | None = None
