from app.dominio.prospecto.prospecto_condominio.servicio_calculo_reconstruccion import ServicioCalculoReconstruccion
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.calculadora_desglose_reconstruccion import CalculadoraDesgloseReconstruccion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.desglose_reconstruccion_unidad import DesgloseReconstruccionUnidad
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota


class CalcularDesgloseReconstruccionUnidadesUseCase:
    """Calcula el desglose de reconstrucción de las unidades de una oportunidad.

    Toma `ServicioCalculoReconstruccion.calcular_valor_unidades` (valor de
    reconstrucción de las unidades) y lo distribuye por el prorrateo de cada
    unidad; el monto resultante redondeado a la centena superior es el monto
    asegurado sugerido de la unidad. El `prorrateo_pago` de cada unidad
    (monto asegurado sugerido sobre el total sugerido) reparte las primas.

    Los valores son derivados: se calculan bajo demanda y no se persisten,
    de modo que siempre reflejan los datos actuales del condominio.

    Si el prospecto no tiene los datos de reconstrucción devuelve (None, None):
    cada caso de uso decide cómo responder ante un desglose no calculable.
    """

    def __init__(self, repositorio_prospectos: RepositorioProspectos) -> None:
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(
        self,
        id_prospecto: int | None,
        unidades: list[UnidadAlicuota],
    ) -> tuple[list[DesgloseReconstruccionUnidad] | None, float | None]:
        if not unidades:
            return None, None

        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id_prospecto) if id_prospecto else None

        if (
            prospecto is None
            or prospecto.metros_cuadrados is None
            or prospecto.uf_por_metro_cuadrado is None
            or prospecto.porcentaje_depreciacion is None
        ):
            return None, None

        valor_unidades = ServicioCalculoReconstruccion.calcular_valor_unidades_desde_datos(
            prospecto.uf_por_metro_cuadrado,
            prospecto.metros_cuadrados,
            prospecto.porcentaje_depreciacion,
        )

        desglose = CalculadoraDesgloseReconstruccion.calcular(valor_unidades, unidades)
        total = CalculadoraDesgloseReconstruccion.total_monto_asegurado_sugerido(desglose)

        return desglose, total
