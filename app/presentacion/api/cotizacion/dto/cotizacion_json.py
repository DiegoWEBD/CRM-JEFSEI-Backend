from pydantic import BaseModel


class CotizacionJson(BaseModel):
    id: int
    monto_total_asegurado: float 
    tasa_afecta: float 
    tasa_excenta: float 
    tasa_politica: float 
    prima_adicional_asistencia: float 
    prima_afecta: float
    prima_excenta: float
    prima_neta: float
    prima_iva: float
    prima_bruta: float
    company: str 
    fecha_emision: str 
    fecha_vencimiento: str
    nombre_archivo: str | None = None
    archivo_base64: str | None = None