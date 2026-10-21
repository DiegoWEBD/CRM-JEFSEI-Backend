from decimal import Decimal, ROUND_CEILING


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

    @staticmethod
    def calcular_valor_unidades(
        valor_reconstruccion_depreciacion: float
    ) -> float:
        return round(valor_reconstruccion_depreciacion * 0.5)

    @staticmethod
    def calcular_valor_unidades_desde_datos(
        uf_por_metro_cuadrado: float,
        metros_cuadrados: float,
        porcentaje_depreciacion: float
    ) -> float:
        valor_reconstruccion = ServicioCalculoReconstruccion.calcular_valor_reconstruccion(
            uf_por_metro_cuadrado, metros_cuadrados
        )
        valor_reconstruccion_depreciacion = ServicioCalculoReconstruccion.calcular_valor_reconstruccion_depreciacion(
            valor_reconstruccion, porcentaje_depreciacion
        )
        return ServicioCalculoReconstruccion.calcular_valor_unidades(valor_reconstruccion_depreciacion)

    @staticmethod
    def redondear_centena_superior(valor: float) -> int:
        """Redondea al múltiplo de 100 igual o superior (1459.78 -> 1500, 1500 -> 1500)."""

        if valor <= 0:
            return 0

        centenas = (Decimal(str(valor)) / 100).to_integral_value(rounding=ROUND_CEILING)

        return int(centenas) * 100
