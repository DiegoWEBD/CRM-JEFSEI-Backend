from pydantic import BaseModel


class CerrarProcesoComercialRequest(BaseModel):
    ganado: bool
    observacion: str | None