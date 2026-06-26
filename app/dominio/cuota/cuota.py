from datetime import datetime


class Cuota:

    def __init__(
        self,
        numero_cuota: int,
        fecha_vencimiento: datetime,
        pagado: bool,
        fecha_pago: datetime | None
    ):
        self.numero_cuota = numero_cuota
        self.fecha_pago = fecha_pago
        self.fecha_vencimiento = fecha_vencimiento
        self.pagado = pagado