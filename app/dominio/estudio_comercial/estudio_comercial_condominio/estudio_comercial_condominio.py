from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial


class EstudioComercialCondominio:

    def __init__(
        self,
        cantidad_cuotas: int,
        valor_uf: float,
        detalles: list[DetalleEstudioComercial]
    ):
        self.cantidad_cuotas = cantidad_cuotas
        self.detalles = detalles
        self.valor_uf = valor_uf