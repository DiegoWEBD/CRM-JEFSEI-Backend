from pydantic import BaseModel

from app.presentacion.api.cotizacion.dto.cotizacion_json import CotizacionJson


class DetalleEstudioComercialCondominioJson(BaseModel):
    cotizacion: CotizacionJson
    porcentaje_infraseguro: float
    iva_prima_afecta: float
    prima_neta: float
    prima_bruta: float