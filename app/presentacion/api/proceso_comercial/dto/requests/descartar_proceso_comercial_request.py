from pydantic import BaseModel


class DescartarProcesoComercialRequest(BaseModel):
    observacion: str | None
