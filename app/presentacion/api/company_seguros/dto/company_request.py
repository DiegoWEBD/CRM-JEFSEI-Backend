from pydantic import BaseModel


class CrearCompanyRequest(BaseModel):
    nombre: str


class ActualizarCompanyRequest(BaseModel):
    nombre: str
