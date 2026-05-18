from app.dominio.estudio_comercial.detalle_estudio_comercial.detalle_estudio_comercial import DetalleEstudioComercial


class EstudioComercialCondominio:

    def __init__(
        self,
        monto_asegurado_actual: float | None,
        metros_cuadrados_construidos: float,
        uf_por_metro_cuadrado: float,
        porcentaje_depreciacion: float,
        porcentaje_espacios_comunes: float,
        cantidad_cuotas: int,
        valor_uf: float,
        detalles: list[DetalleEstudioComercial]
    ):
        self.monto_asegurado_actual = monto_asegurado_actual
        self.metros_cuadrados_construidos = metros_cuadrados_construidos
        self.uf_por_metro_cuadrado = uf_por_metro_cuadrado
        self.porcentaje_depreciacion = porcentaje_depreciacion
        self.cantidad_cuotas = cantidad_cuotas
        self.porcentaje_espacios_comunes = porcentaje_espacios_comunes
        self.detalles = detalles
        self.valor_uf = valor_uf