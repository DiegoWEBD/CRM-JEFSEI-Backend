from decimal import Decimal, ROUND_HALF_UP

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.servicio_calculo_primas import ServicioCalculoPrimas
from app.dominio.estudio_comercial.desglose_unidades.desglose_unidad import DesgloseUnidad
from app.dominio.estudio_comercial.desglose_unidades.totales_prima import TotalesPrima
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota


class CalculadoraDesgloseUnidades:
    """Prorratea los valores totales de cada cotización sobre las unidades de la alícuota."""

    DECIMALES = Decimal('0.01')

    @staticmethod
    def calcular_totales(cotizacion: Cotizacion, monto_base: float | None = None) -> TotalesPrima:
        """Primer cálculo: primas totales de la cotización a partir de sus tasas.

        Si no se indica un monto base, se usa el monto total por el que se cotizó.
        """

        monto_asegurado = cotizacion.monto_total_asegurado if monto_base is None else monto_base

        prima_afecta = ServicioCalculoPrimas.calcular_prima_afecta(
            monto_asegurado,
            cotizacion.tasa_afecta,
            cotizacion.tasa_politica,
            cotizacion.asistencia_afecta,
        )
        prima_excenta = ServicioCalculoPrimas.calcular_prima_excenta(
            monto_asegurado,
            cotizacion.tasa_excenta,
            cotizacion.asistencia_excenta,
        )
        prima_iva = ServicioCalculoPrimas.calcular_iva_prima_afecta(prima_afecta)
        prima_neta = ServicioCalculoPrimas.calcular_prima_neta(prima_afecta, prima_excenta)
        prima_bruta = ServicioCalculoPrimas.calcular_prima_bruta(prima_neta, prima_iva)

        return TotalesPrima(
            monto_asegurado=monto_asegurado,
            prima_afecta=prima_afecta,
            prima_excenta=prima_excenta,
            prima_iva=prima_iva,
            prima_neta=prima_neta,
            prima_bruta=prima_bruta,
        )

    @staticmethod
    def calcular_desglose(
        totales: TotalesPrima,
        unidades: list[UnidadAlicuota],
    ) -> list[DesgloseUnidad]:
        """Multiplica los totales ya redondeados por el prorrateo decimal de cada unidad."""

        return [
            CalculadoraDesgloseUnidades.calcular_desglose_unidad(totales, unidad)
            for unidad in unidades
        ]

    @staticmethod
    def calcular_desglose_unidad(totales: TotalesPrima, unidad: UnidadAlicuota) -> DesgloseUnidad:
        prorrateo = unidad.prorrateo  # fracción decimal: 0,0085 representa 0,85 %

        return DesgloseUnidad(
            identificador_unidad=unidad.identificador_unidad,
            prorrateo=prorrateo,
            monto_asegurado=CalculadoraDesgloseUnidades._prorratear(totales.monto_asegurado, prorrateo),
            prima_afecta=CalculadoraDesgloseUnidades._prorratear(totales.prima_afecta, prorrateo),
            prima_excenta=CalculadoraDesgloseUnidades._prorratear(totales.prima_excenta, prorrateo),
            prima_neta=CalculadoraDesgloseUnidades._prorratear(totales.prima_neta, prorrateo),
            prima_iva=CalculadoraDesgloseUnidades._prorratear(totales.prima_iva, prorrateo),
            prima_bruta=CalculadoraDesgloseUnidades._prorratear(totales.prima_bruta, prorrateo),
        )

    @staticmethod
    def _prorratear(total: float, prorrateo: float) -> float:
        resultado = Decimal(str(total)) * Decimal(str(prorrateo))
        return float(resultado.quantize(CalculadoraDesgloseUnidades.DECIMALES, rounding=ROUND_HALF_UP))
