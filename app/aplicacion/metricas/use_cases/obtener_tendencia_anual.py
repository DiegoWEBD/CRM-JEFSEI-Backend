from app.aplicacion.metricas.dto.metricas_dashboard_dto import TendenciaMesDto
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerTendenciaAnualUseCase:
    """Prima neta por mes del año consultado, hasta el mes seleccionado.

    La serie siempre cubre enero..mes del año informado (inclusive), con
    `prima_neta = 0.0` en los meses sin producción, y `mes` en formato
    `YYYY-MM`.
    """

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> list[TendenciaMesDto]:
        tendencia_raw = self.repositorio.obtener_tendencia_anual(year, mes)
        por_mes = {
            r["mes"]: float(r["prima_neta"])
            for r in tendencia_raw
        }
        return [
            TendenciaMesDto(
                mes=f'{year}-{mes_num:02d}',
                prima_neta=por_mes.get(f'{year}-{mes_num:02d}', 0.0),
            )
            for mes_num in range(1, mes + 1)
        ]
