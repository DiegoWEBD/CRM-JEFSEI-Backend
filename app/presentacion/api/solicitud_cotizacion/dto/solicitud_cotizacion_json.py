from pydantic import BaseModel

from app.presentacion.api.cotizacion.dto.cotizacion_json import CotizacionJson


class SolicitudCotizacionJson(BaseModel):
    id: int
    fecha: str 
    prioridad: str 
    cotizaciones: list[CotizacionJson]