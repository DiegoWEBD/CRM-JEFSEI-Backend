from pydantic import BaseModel


class CotizacionJson(BaseModel):
    id: int
    monto_total_asegurado: float 
    tasa_afecta: float 
    tasa_excenta: float 
    tasa_politica: float 
    prima_adicional_asistencia: float 
    prima_afecta: float | None = None
    prima_excenta: float | None = None
    prima_neta: float | None = None
    prima_iva: float | None = None
    prima_bruta: float | None = None
    company: str 
    fecha_emision: str 
    fecha_vencimiento: str
    nombre_archivo: str | None = None
    archivo_base64: str | None = None