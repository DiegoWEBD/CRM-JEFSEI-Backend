from datetime import datetime


class Poliza:
    def __init__(
        self, 
        numero_poliza: str, 
        rut_cliente: str, 
        tipo: str, 
        inicio_vigencia: datetime,
        fin_vigencia: datetime
    ):
        self.numero_poliza = numero_poliza
        self.rut_cliente = rut_cliente
        self.tipo = tipo
        self.inicio_vigencia = inicio_vigencia
        self.fin_vigencia = fin_vigencia