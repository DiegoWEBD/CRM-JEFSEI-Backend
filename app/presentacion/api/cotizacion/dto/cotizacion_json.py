from pydantic import BaseModel

from app.presentacion.api.cotizacion.dto.estado_cotizacion import EstadoCotizacion


class CotizacionJson(BaseModel):
    id: int
    monto_total_asegurado: float 
    tasa_afecta: float 
    tasa_excenta: float 
    tasa_politica: float 
    asistencia_afecta: float
    asistencia_excenta: float
    prima_afecta: float
    prima_excenta: float
    prima_neta: float
    prima_iva: float
    prima_bruta: float
    company: str 
    fecha_emision: str 
    fecha_vencimiento: str
    estado: EstadoCotizacion
    nombre_archivo: str | None = None
    archivo_base64: str | None = None