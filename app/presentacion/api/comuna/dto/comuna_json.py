from pydantic import BaseModel


class ComunaJson(BaseModel):
    id: int
    nombre: str