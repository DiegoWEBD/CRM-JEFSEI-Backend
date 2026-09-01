from pydantic import BaseModel


class ActualizarProductoRequest(BaseModel):
    nombre: str
    id_linea_negocio: int
    codigo: str | None = None
