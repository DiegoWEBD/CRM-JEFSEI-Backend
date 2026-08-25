from pydantic import BaseModel


class ActualizarPolizaRequest(BaseModel):
    tipo: str
    prima_neta: float
    comision_corredora_pct: float
    fecha_emision: str | None
    inicio_vigencia: str | None
    fin_vigencia: str | None
    id_company: int | None
