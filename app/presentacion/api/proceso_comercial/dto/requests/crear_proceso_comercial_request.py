from pydantic import BaseModel


class CrearProcesoComercialRequest(BaseModel):
    id_prospecto: int
    tipo: str