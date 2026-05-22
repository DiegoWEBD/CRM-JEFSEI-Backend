from pydantic import BaseModel


class CotizacionJson(BaseModel):
    id: int
    monto_total_asegurado: float 
    tasa_afecta: float 
    tasa_excenta: float 
    tasa_politica: float 
    prima_adicional_asistencia: float 
    company: str 
    fecha_emision: str 
    fecha_vencimiento: str