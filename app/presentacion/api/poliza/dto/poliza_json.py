from pydantic import BaseModel

from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.presentacion.api.company_seguros.dto.company_seguros_json import CompanySegurosJson


class PolizaJson(BaseModel):
    numero_poliza: str 
    id_proceso_comercial: int
    tipo: str 
    nombre_producto: str
    company: CompanySegurosJson | None
    prima_neta: float
    comision_corredora_pct: float
    fecha_emision: str | None
    inicio_vigencia: str | None
    fin_vigencia: str | None
    estado: EstadoPoliza
    renovacion_cotizada: bool