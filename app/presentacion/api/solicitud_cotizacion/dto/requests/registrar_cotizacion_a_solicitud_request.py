from dataclasses import dataclass
from datetime import datetime


@dataclass
class RegistrarCotizacionASolicitudRequest:
    monto_total_asegurado: float 
    tasa_afecta: float 
    tasa_excenta: float 
    tasa_politica: float 
    prima_adicional_asistencia: float 
    id_company: int 
    fecha_emision: datetime 
    fecha_vencimiento: datetime