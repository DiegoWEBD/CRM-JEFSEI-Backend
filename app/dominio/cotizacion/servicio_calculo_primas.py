class ServicioCalculoPrimas:
    """Calcula las primas de una cotización sin redondear.

    Los cálculos mantienen precisión completa para no propagar errores de
    redondeo; el redondeo se aplica únicamente al mostrar cada resultado final.
    """

    IVA_RATE: float = 0.19

    @staticmethod
    def calcular_prima_afecta(
        monto_asegurado: float,
        tasa_afecta: float,
        tasa_politica: float,
        asistencia_afecta: float
    ) -> float:
        return (monto_asegurado / 1000 * (tasa_afecta + tasa_politica)) + asistencia_afecta

    @staticmethod
    def calcular_prima_excenta(
        monto_asegurado: float,
        tasa_excenta: float,
        asistencia_excenta: float
    ) -> float:
        return (monto_asegurado * tasa_excenta / 1000) + asistencia_excenta

    @staticmethod
    def calcular_iva_prima_afecta(prima_afecta: float) -> float:
        return prima_afecta * ServicioCalculoPrimas.IVA_RATE

    @staticmethod
    def calcular_prima_neta(prima_afecta: float, prima_excenta: float) -> float:
        return prima_afecta + prima_excenta

    @staticmethod
    def calcular_prima_bruta(prima_neta: float, iva_prima_afecta: float) -> float:
        return prima_neta + iva_prima_afecta

    @staticmethod
    def calcular_tasas_desde_primas(
        prima_afecta: float,
        prima_excenta: float,
        monto_total_asegurado: float
    ) -> tuple[float, float]:
        tasa_afecta = (prima_afecta / monto_total_asegurado) * 1000 if monto_total_asegurado else 0.0
        tasa_excenta = (prima_excenta / monto_total_asegurado) * 1000 if monto_total_asegurado else 0.0
        return tasa_afecta, tasa_excenta
