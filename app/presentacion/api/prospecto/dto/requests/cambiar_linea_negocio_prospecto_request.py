from pydantic import BaseModel


class CambiarLineaNegocioProspectoRequest(BaseModel):
    id_linea_negocio: int
