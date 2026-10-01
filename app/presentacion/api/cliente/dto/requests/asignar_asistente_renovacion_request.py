from pydantic import BaseModel


class AsignarAsistenteRenovacionRequest(BaseModel):
    rut_as_renovacion: str | None = None
