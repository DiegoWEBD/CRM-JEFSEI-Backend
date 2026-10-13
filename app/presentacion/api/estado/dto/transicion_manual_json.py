from pydantic import BaseModel


class TransicionManualJson(BaseModel):
    codigo: str
    nombre: str
    accion_requerida: str | None