from pydantic import BaseModel

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.poliza.poliza import Poliza


class EvaluacionRiesgoJson(BaseModel):
    uf_por_metro_cuadrado: float | None
    porcentaje_depreciacion: float | None
    porcentaje_espacios_comunes: float | None
    observaciones: str | None  
    #cotizaciones: list[Cotizacion] = []
    #poliza: Poliza | None  
    #plan_pago: PlanPago | None 
    #estudios: list[EstudioComercialCondominio] | None 