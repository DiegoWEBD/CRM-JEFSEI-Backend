from pydantic import BaseModel

from app.presentacion.api.cotizacion.dto.cotizacion_json import CotizacionJson
from app.presentacion.api.estudio_comercial.dto.estudio_comercial_condominio_json import EstudioComercialCondominioJson


class EvaluacionRiesgoJson(BaseModel):
    uf_por_metro_cuadrado: float | None
    porcentaje_depreciacion: float | None
    porcentaje_espacios_comunes: float | None
    observaciones: str | None  
    cotizaciones: list[CotizacionJson]
    estudio: EstudioComercialCondominioJson | None
    #poliza: Poliza | None  
    #plan_pago: PlanPago | None 
    #estudios: list[EstudioComercialCondominio] | None 