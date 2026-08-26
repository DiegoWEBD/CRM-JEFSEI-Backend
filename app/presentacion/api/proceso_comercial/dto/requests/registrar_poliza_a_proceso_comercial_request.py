from pydantic import BaseModel


class RegistrarPolizaAProcesoComercialRequest(BaseModel):
    numero_poliza: str 
    tipo: str
    id_company: int
    prima_neta: float
    comision_corredora_pct: float
    fecha_emision: str | None
    inicio_vigencia: str | None
    fin_vigencia: str | None