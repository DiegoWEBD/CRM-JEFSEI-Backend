class ServicioCalculoPrimas:

    IVA_RATE: float = 0.19
    DECIMALES: int = 2

    @staticmethod
    def calcular_prima_afecta(
        monto_asegurado: float,
        tasa_afecta: float,
        tasa_politica: float,
        asistencia_afecta: float
    ) -> float:
        return round(
            (monto_asegurado / 1000 * (tasa_afecta + tasa_politica)) + asistencia_afecta,
            ServicioCalculoPrimas.DECIMALES
        )

    @staticmethod
    def calcular_prima_excenta(
        monto_asegurado: float,
        tasa_excenta: float,
        asistencia_excenta: float
    ) -> float:
        return round(
            (monto_asegurado * tasa_excenta / 1000) + asistencia_excenta,
            ServicioCalculoPrimas.DECIMALES
        )

    @staticmethod
    def calcular_iva_prima_afecta(prima_afecta: float) -> float:
        return round(prima_afecta * ServicioCalculoPrimas.IVA_RATE, ServicioCalculoPrimas.DECIMALES)

    @staticmethod
    def calcular_prima_neta(prima_afecta: float, prima_excenta: float) -> float:
        return round(prima_afecta + prima_excenta, ServicioCalculoPrimas.DECIMALES)

    @staticmethod
    def calcular_prima_bruta(prima_neta: float, iva_prima_afecta: float) -> float:
        return round(prima_neta + iva_prima_afecta, ServicioCalculoPrimas.DECIMALES)

    @staticmethod
    def calcular_tasas_desde_primas(
        prima_afecta: float,
        prima_excenta: float,
        monto_total_asegurado: float
    ) -> tuple[float, float]:
        tasa_afecta = (prima_afecta / monto_total_asegurado) * 1000 if monto_total_asegurado else 0.0
        tasa_excenta = (prima_excenta / monto_total_asegurado) * 1000 if monto_total_asegurado else 0.0
        return tasa_afecta, tasa_excenta
