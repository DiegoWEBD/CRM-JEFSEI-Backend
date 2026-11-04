from pydantic import BaseModel


class LineaNegocioJson(BaseModel):
    id: int
    nombre: str
    codigo: str | None = None
    productos: list[str]
