from datetime import datetime, timezone


class Cuota:

    def __init__(
        self,
        id: int | None = None,
        numero_cuota: int = 0,
        fecha_vencimiento: datetime | None = None,
        pagado: bool = False,
        fecha_pago: datetime | None = None
    ):
        self.id = id
        self.numero_cuota = numero_cuota
        self.fecha_pago = fecha_pago
        self.fecha_vencimiento = fecha_vencimiento
        self.pagado = pagado

    def marcar_como_pagada(self) -> None:
        self.pagado = True
        self.fecha_pago = datetime.now(timezone.utc)