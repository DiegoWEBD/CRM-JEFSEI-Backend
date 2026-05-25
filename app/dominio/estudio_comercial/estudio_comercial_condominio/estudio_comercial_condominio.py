from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial


class EstudioComercialCondominio:

    def __init__(
        self,
        cantidad_cuotas: int,
        valor_uf: float,
        monto_asegurado_actual: float | None,
        porcentaje_infrasegurdo: float | None,
        detalles: list[DetalleEstudioComercial]
    ):
        self.cantidad_cuotas = cantidad_cuotas
        self.detalles = detalles
        self.valor_uf = valor_uf
        self.monto_asegurado_actual = monto_asegurado_actual
        self.porcentaje_infraseguro = porcentaje_infrasegurdo