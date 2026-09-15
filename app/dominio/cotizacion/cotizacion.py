from app.dominio.company_seguros.company_seguros import CompanySeguros
from datetime import datetime


class Cotizacion:
    def __init__(
        self, 
        id: int | None,
        monto_total_asegurado: float, 
        tasa_afecta: float, 
        tasa_excenta: float, 
        tasa_politica: float, 
        asistencia_afecta: float,
        asistencia_excenta: float,
        company: CompanySeguros, 
        fecha_emision: datetime, 
        fecha_vencimiento: datetime,
        prima_afecta: float,
        prima_excenta: float,
        prima_neta: float,
        prima_iva: float,
        prima_bruta: float,
        nombre_archivo: str | None = None,
    ):
        self.id = id
        self.asistencia_afecta = asistencia_afecta
        self.asistencia_excenta = asistencia_excenta
        self.tasa_afecta = tasa_afecta
        self.tasa_excenta = tasa_excenta
        self.tasa_politica = tasa_politica
        self.company = company
        self.fecha_emision = fecha_emision
        self.fecha_vencimiento = fecha_vencimiento
        self.monto_total_asegurado = monto_total_asegurado
        self.nombre_archivo = nombre_archivo
        self.prima_afecta = prima_afecta
        self.prima_excenta = prima_excenta
        self.prima_neta = prima_neta
        self.prima_iva = prima_iva
        self.prima_bruta = prima_bruta