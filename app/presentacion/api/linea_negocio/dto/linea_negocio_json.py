from pydantic import BaseModel


class LineaNegocioJson(BaseModel):
    id: int
    nombre: str
    productos: list[str]