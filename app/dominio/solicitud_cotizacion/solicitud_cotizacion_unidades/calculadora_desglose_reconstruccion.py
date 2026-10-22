from decimal import Decimal, ROUND_HALF_UP

from app.dominio.prospecto.prospecto_condominio.servicio_calculo_reconstruccion import ServicioCalculoReconstruccion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.desglose_reconstruccion_unidad import DesgloseReconstruccionUnidad
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota


class CalculadoraDesgloseReconstruccion:
    """Distribuye el valor de reconstrucción de las unidades sobre la alícuota.

    Por cada unidad: monto de reconstrucción = valor de las unidades × prorrateo,
    y monto asegurado sugerido = ese monto redondeado a la centena superior.

    El `prorrateo_pago` de cada unidad (monto asegurado sugerido de la unidad
    sobre el total sugerido) es el que reparte las primas entre los propietarios.
    """

    DECIMALES = Decimal('0.01')

    @staticmethod
    def calcular(
        valor_unidades: float,
        unidades: list[UnidadAlicuota],
    ) -> list[DesgloseReconstruccionUnidad]:
        desglose = [
            CalculadoraDesgloseReconstruccion.calcular_unidad(valor_unidades, unidad)
            for unidad in unidades
        ]

        total = CalculadoraDesgloseReconstruccion.total_monto_asegurado_sugerido(desglose)

        for item in desglose:
            item.prorrateo_pago = (
                float(Decimal(str(item.monto_asegurado_sugerido)) / Decimal(str(total)))
                if total > 0
                else 0.0
            )

        return desglose

    @staticmethod
    def calcular_unidad(valor_unidades: float, unidad: UnidadAlicuota) -> DesgloseReconstruccionUnidad:
        monto_reconstruccion = float(
            (Decimal(str(valor_unidades)) * Decimal(str(unidad.prorrateo))).quantize(
                CalculadoraDesgloseReconstruccion.DECIMALES, rounding=ROUND_HALF_UP
            )
        )
        monto_asegurado_sugerido = float(
            ServicioCalculoReconstruccion.redondear_centena_superior(monto_reconstruccion)
        )

        return DesgloseReconstruccionUnidad(
            identificador_unidad=unidad.identificador_unidad,
            prorrateo=unidad.prorrateo,
            fila_origen=unidad.fila_origen,
            monto_reconstruccion=monto_reconstruccion,
            monto_asegurado_sugerido=monto_asegurado_sugerido,
            prorrateo_pago=0.0,
        )

    @staticmethod
    def total_monto_asegurado_sugerido(desglose: list[DesgloseReconstruccionUnidad]) -> float:
        return round(sum(item.monto_asegurado_sugerido for item in desglose), 2)
