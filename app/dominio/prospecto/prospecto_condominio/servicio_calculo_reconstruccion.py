class ServicioCalculoReconstruccion:

    FACTOR_IVA = 1.19

    @staticmethod
    def calcular_valor_reconstruccion(
        uf_por_metro_cuadrado: float,
        metros_cuadrados: float
    ) -> float:
        return round(uf_por_metro_cuadrado * metros_cuadrados * ServicioCalculoReconstruccion.FACTOR_IVA)

    @staticmethod
    def calcular_valor_reconstruccion_depreciacion(
        valor_reconstruccion: float,
        porcentaje_depreciacion: float
    ) -> float:
        return round(valor_reconstruccion * (1 - porcentaje_depreciacion))

    @staticmethod
    def calcular_valor_espacio_comun(
        valor_reconstruccion_depreciacion: float,
        porcentaje_espacios_comunes: float
    ) -> float:
        return round(valor_reconstruccion_depreciacion * porcentaje_espacios_comunes)
