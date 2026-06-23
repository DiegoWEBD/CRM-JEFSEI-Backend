from pydantic import BaseModel


class CompanySegurosJson(BaseModel):
    id: int
    nombre: str
