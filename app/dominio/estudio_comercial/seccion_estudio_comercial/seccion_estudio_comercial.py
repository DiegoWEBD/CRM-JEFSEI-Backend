from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial


class SeccionEstudioComercial:

    def __init__(
        self,
        titulo: str,
        monto_asegurado: float,
        numero_propietarios: int | None,
        detalles: list[DetalleEstudioComercial]
    ):
        self.titulo = titulo
        self.monto_asegurado = monto_asegurado
        self.numero_propietarios = numero_propietarios
        self.detalles = detalles