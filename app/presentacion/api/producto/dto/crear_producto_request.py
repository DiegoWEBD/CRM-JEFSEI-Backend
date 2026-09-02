from pydantic import BaseModel


class CrearProductoRequest(BaseModel):
    nombre: str
    id_linea_negocio: int
