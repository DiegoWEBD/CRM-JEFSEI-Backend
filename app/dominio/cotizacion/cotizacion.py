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
        prima_adicional_asistencia: float, 
        company: CompanySeguros, 
        fecha_emision: datetime, 
        fecha_vencimiento: datetime,
        nombre_archivo: str | None = None,
        prima_afecta: float | None = None,
        prima_excenta: float | None = None,
        prima_neta: float | None = None,
        prima_iva: float | None = None,
        prima_bruta: float | None = None,
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
        self.nombre_archivo = nombre_archivo
        self.prima_afecta = prima_afecta
        self.prima_excenta = prima_excenta
        self.prima_neta = prima_neta
        self.prima_iva = prima_iva
        self.prima_bruta = prima_bruta