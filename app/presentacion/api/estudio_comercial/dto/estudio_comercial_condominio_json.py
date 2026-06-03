from pydantic import BaseModel

from app.presentacion.api.detalle_estudio_comercial_condominio.dto.detalle_estudio_comercial_condominio_json import DetalleEstudioComercialCondominioJson


class EstudioComercialCondominioJson(BaseModel):
    cantidad_cuotas: int
    valor_uf: float
    detalles: list[DetalleEstudioComercialCondominioJson]