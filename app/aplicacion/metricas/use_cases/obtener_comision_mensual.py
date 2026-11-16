from app.aplicacion.metricas.dto.metricas_dashboard_dto import ComisionMensualDto
from app.aplicacion.metricas.periodo import etiqueta_mes
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerComisionMensualUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> ComisionMensualDto:
        return ComisionMensualDto(
            total_comision=self.repositorio.obtener_comision_mes(year, mes),
            mes_label=etiqueta_mes(year, mes),
        )
