from pydantic import BaseModel


class RolJson(BaseModel):
    codigo: str
    nombre: str