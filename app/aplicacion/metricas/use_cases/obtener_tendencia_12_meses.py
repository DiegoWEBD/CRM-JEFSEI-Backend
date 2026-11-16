from app.aplicacion.metricas.dto.metricas_dashboard_dto import TendenciaMesDto
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerTendencia12MesesUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> list[TendenciaMesDto]:
        tendencia_raw = self.repositorio.obtener_tendencia_12_meses(year, mes)
        return [
            TendenciaMesDto(mes=r["mes"], prima_neta=float(r["prima_neta"]))
            for r in tendencia_raw
        ]
