from pydantic import BaseModel


class AsignarEjecutivoRenovacionRequest(BaseModel):
    rut_ej_renovacion: str | None = None
