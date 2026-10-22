from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany


class ServicioCalculoValorCuota:
    """Calcula el valor de la cuota de financiamiento de una prima bruta.

    Usa el factor de cuotas de la compañía cuando existe uno para la cantidad
    de cuotas pedida; si no, aplica la fórmula genérica de anualidad
    (tasa 0,5 % mensual).
    """

    TASA_FACTOR_GENERICO = 0.005

    @staticmethod
    def calcular_valor_cuota(
        prima_bruta: float,
        cantidad_cuotas: int,
        factores_cuotas: list[FactorCuotasCompany],
    ) -> float:
        factor = next(
            (
                factor_cuota.factor
                for factor_cuota in factores_cuotas
                if factor_cuota.numero_cuotas == cantidad_cuotas
            ),
            None,
        )

        if factor is not None:
            return prima_bruta * factor

        return ServicioCalculoValorCuota.calcular_con_factor_generico(prima_bruta, cantidad_cuotas)

    @staticmethod
    def calcular_con_factor_generico(prima_bruta: float, cantidad_cuotas: int) -> float:
        tasa = ServicioCalculoValorCuota.TASA_FACTOR_GENERICO

        cuota = (tasa * prima_bruta) / (1 - (1 + tasa) ** -cantidad_cuotas)

        return cuota

    @staticmethod
    def calcular_valor_cuota_pesos(valor_cuota: float, valor_uf: float) -> float:
        """Convierte la cuota en UF a pesos sin redondear.

        El redondeo al peso se aplica únicamente al mostrar el resultado final.
        """
        return valor_cuota * valor_uf
