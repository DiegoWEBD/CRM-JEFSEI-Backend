from datetime import datetime


class Pago:

    def __init__(
        self,
        monto: float,
        metodo_pago: str,
        fecha: datetime
    ):
        self.monto = monto
        self.metodo_pago = metodo_pago
        self.fecha = fecha