class EstudioComercial:

    def __init__(
        self,
        monto_asegurado_actual: float,
        infraseguro_primer_ejemplo: float,
        infraseguro_segundo_ejemplo: float,
        metros_cuadrados_construidos: float,
        valor_uf_por_metro_cuadrado: float,
        porcentaje_depreciacion: float,
        cantidad_cuotas: int,
        porcentaje_bienes_espacios_comunes: float,
        valor_total_reconstruccion_iva: float,
        valor_total_reconstruccion_depreciacion_iva: float,
        monto_asegurado_sugerido: float,
        infraseguro_actual: float,
        monto_asegurado_primer_ejemplo: float,
        monto_asegurado_segundo_ejemplo: float
    ):
        self.monto_asegurado_actual = monto_asegurado_actual
        self.infraseguro_primer_ejemplo = infraseguro_primer_ejemplo
        self.infraseguro_segundo_ejemplo = infraseguro_segundo_ejemplo
        self.metros_cuadrados_construidos = metros_cuadrados_construidos
        self.valor_uf_por_metro_cuadrado = valor_uf_por_metro_cuadrado
        self.porcentaje_depreciacion = porcentaje_depreciacion
        self.cantidad_cuotas = cantidad_cuotas
        self.porcentaje_bienes_espacios_comunes = porcentaje_bienes_espacios_comunes
        self.valor_total_reconstruccion_iva = valor_total_reconstruccion_iva
        self.valor_total_reconstruccion_depreciacion_iva = valor_total_reconstruccion_depreciacion_iva
        self.monto_asegurado_sugerido = monto_asegurado_sugerido
        self.infraseguro_actual = infraseguro_actual
        self.monto_asegurado_primer_ejemplo = monto_asegurado_primer_ejemplo
        self.monto_asegurado_segundo_ejemplo = monto_asegurado_segundo_ejemplo