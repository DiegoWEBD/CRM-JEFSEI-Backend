from pydantic import BaseModel


class RegistrarPolizaAProcesoComercialRequest(BaseModel):
    numero_poliza: str 
    tipo: str
    id_company: int
    prima_neta: float
    comision_corredora_pct: float
    fecha_emision: str
    inicio_vigencia: str
    fin_vigencia: str