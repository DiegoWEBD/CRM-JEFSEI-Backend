from datetime import datetime

from app.dominio.pago.pago import Pago


class Cuota:

    def __init__(
        self,
        numero_cuota: int,
        monto: float,
        fecha_pago: datetime,
        pago: Pago | None = None
    ):
        self.numero_cuota = numero_cuota
        self.monto = monto
        self.fecha_pago = fecha_pago
        self.pago = pago