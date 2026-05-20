from app.dominio.company_seguros.company_seguros import CompanySeguros
from datetime import datetime

from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio

class Cotizacion:
    def __init__(
        self, 
        id: int, 
        prima_neta: float, 
        tasa_interes: float, 
        company: CompanySeguros, 
        fecha_emision: datetime, 
        fecha_vencimiento: datetime,
        estudios: list[EstudioComercialCondominio] | None = None
    ):
        self.id = id
        self.prima_neta = prima_neta
        self.tasa_interes = tasa_interes
        self.company = company
        self.fecha_emision = fecha_emision
        self.fecha_vencimiento = fecha_vencimiento
        self.estudios = estudios