from datetime import datetime


class Poliza:
    def __init__(
        self, 
        numero_poliza: str, 
        tipo: str, 
        company: str | None,
        prima_neta: float,
        comision_corredora_pct: float,
        fecha_emision: datetime,
        inicio_vigencia: datetime,
        fin_vigencia: datetime
    ):
        self.numero_poliza = numero_poliza
        self.tipo = tipo
        self.inicio_vigencia = inicio_vigencia
        self.fin_vigencia = fin_vigencia
        self.company = company
        self.prima_neta = prima_neta
        self.fecha_emision = fecha_emision
        self.comision_corredora_pct = comision_corredora_pct