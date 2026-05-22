from app.dominio.company_seguros.company_seguros import CompanySeguros
from datetime import datetime


class Cotizacion:
    def __init__(
        self, 
        id: int,
        monto_total_asegurado: float, 
        tasa_afecta: float, 
        tasa_excenta: float, 
        tasa_politica: float, 
        prima_adicional_asistencia: float, 
        company: CompanySeguros, 
        fecha_emision: datetime, 
        fecha_vencimiento: datetime,
    ):
        self.id = id
        self.prima_adicional_asistencia = prima_adicional_asistencia
        self.tasa_afecta = tasa_afecta
        self.tasa_excenta = tasa_excenta
        self.tasa_politica = tasa_politica
        self.company = company
        self.fecha_emision = fecha_emision
        self.fecha_vencimiento = fecha_vencimiento
        self.monto_total_asegurado = monto_total_asegurado