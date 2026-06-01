from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial


class EstudioComercialCondominio:

    def __init__(
        self,
        cantidad_cuotas: int,
        valor_uf: float,
        monto_asegurado_actual: float | None,
        porcentaje_infraseguro: float | None,
        detalles_monto_asegurado_actual: list[DetalleEstudioComercial],
        detalles_monto_asegurado_sugerido: list[DetalleEstudioComercial],
        detalles_monto_asegurado_primer_ejemplo: list[DetalleEstudioComercial],
        detalles_monto_asegurado_segundo_ejemplo: list[DetalleEstudioComercial]
    ):
        self.cantidad_cuotas = cantidad_cuotas
        self.valor_uf = valor_uf
        self.monto_asegurado_actual = monto_asegurado_actual
        self.porcentaje_infraseguro = porcentaje_infraseguro
        self.detalles_monto_asegurado_actual = detalles_monto_asegurado_actual
        self.detalles_monto_asegurado_sugerido = detalles_monto_asegurado_sugerido
        self.detalles_monto_asegurado_primer_ejemplo = detalles_monto_asegurado_primer_ejemplo
        self.detalles_monto_asegurado_segundo_ejemplo = detalles_monto_asegurado_segundo_ejemplo