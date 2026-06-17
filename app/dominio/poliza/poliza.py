from datetime import datetime

from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza


class Poliza:
    def __init__(
        self, 
        numero_poliza: str, 
        tipo: str, 
        nombre_producto: str,
        company: str | None,
        prima_neta: float,
        comision_corredora_pct: float,
        fecha_emision: datetime | None,
        inicio_vigencia: datetime | None,
        fin_vigencia: datetime | None,
        estado: EstadoPoliza,
        renovacion_cotizada: bool
    ):
        self.numero_poliza = numero_poliza
        self.tipo = tipo
        self.inicio_vigencia = inicio_vigencia
        self.fin_vigencia = fin_vigencia
        self.company = company
        self.prima_neta = prima_neta
        self.fecha_emision = fecha_emision
        self.comision_corredora_pct = comision_corredora_pct
        self.nombre_producto = nombre_producto
        self.estado = estado
        self.renovacion_cotizada = renovacion_cotizada