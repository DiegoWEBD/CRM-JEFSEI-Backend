from pydantic import BaseModel

from app.presentacion.api.linea_negocio.dto.codigo_linea_negocio import CodigoLineaNegocio


class CambiarLineaNegocioProspectoRequest(BaseModel):
    codigo_linea_negocio: CodigoLineaNegocio
