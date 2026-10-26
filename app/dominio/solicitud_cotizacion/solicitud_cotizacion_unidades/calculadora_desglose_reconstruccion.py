from decimal import Decimal

from app.dominio.prospecto.prospecto_condominio.servicio_calculo_reconstruccion import ServicioCalculoReconstruccion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.desglose_reconstruccion_unidad import DesgloseReconstruccionUnidad
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota


class CalculadoraDesgloseReconstruccion:
    """Distribuye el valor de reconstrucción de las unidades sobre la alícuota.

    Por cada unidad: monto de reconstrucción = valor de las unidades × prorrateo,
    y monto asegurado sugerido = ese monto redondeado a la centena superior.

    El monto asegurado de la unidad es el personalizado si el propietario fijó
    uno explícito; si no, el sugerido. Las unidades descartadas no aportan al
    total.

    El `prorrateo_pago` de cada unidad (monto asegurado de la unidad sobre el
    total de las unidades activas) es el que reparte las primas entre los
    propietarios.
    """

    @staticmethod
    def calcular(
        valor_unidades: float,
        unidades: list[UnidadAlicuota],
    ) -> list[DesgloseReconstruccionUnidad]:
        desglose = [
            CalculadoraDesgloseReconstruccion.calcular_unidad(valor_unidades, unidad)
            for unidad in unidades
        ]

        total = CalculadoraDesgloseReconstruccion.total_monto_asegurado(desglose)

        for item in desglose:
            if item.descartada or total <= 0:
                item.prorrateo_pago = 0.0
            else:
                item.prorrateo_pago = float(
                    Decimal(str(item.monto_asegurado)) / Decimal(str(total))
                )

        return desglose

    @staticmethod
    def calcular_unidad(valor_unidades: float, unidad: UnidadAlicuota) -> DesgloseReconstruccionUnidad:
        # Precisión completa: el redondeo se aplica solo al mostrar el resultado.
        monto_reconstruccion = float(
            Decimal(str(valor_unidades)) * Decimal(str(unidad.prorrateo))
        )
        monto_asegurado_sugerido = float(
            ServicioCalculoReconstruccion.redondear_centena_superior(monto_reconstruccion)
        )

        return DesgloseReconstruccionUnidad(
            id_unidad=unidad.id,
            identificador_unidad=unidad.identificador_unidad,
            prorrateo=unidad.prorrateo,
            fila_origen=unidad.fila_origen,
            monto_reconstruccion=monto_reconstruccion,
            monto_asegurado_sugerido=monto_asegurado_sugerido,
            prorrateo_pago=0.0,
            descartada=unidad.descartada,
            monto_asegurado=unidad.monto_asegurado_efectivo(monto_asegurado_sugerido),
            monto_asegurado_personalizado=unidad.monto_asegurado_personalizado,
        )

    @staticmethod
    def total_monto_asegurado(desglose: list[DesgloseReconstruccionUnidad]) -> float:
        """Monto asegurado total de las unidades activas (personalizado o sugerido)."""

        return round(
            sum(
                item.monto_asegurado or 0.0
                for item in desglose
                if not item.descartada
            ),
            2,
        )

    @staticmethod
    def total_monto_asegurado_sugerido(desglose: list[DesgloseReconstruccionUnidad]) -> float:
        """Suma de los montos sugeridos de las unidades activas (dato informativo)."""

        return round(
            sum(
                item.monto_asegurado_sugerido or 0.0
                for item in desglose
                if not item.descartada
            ),
            2,
        )
