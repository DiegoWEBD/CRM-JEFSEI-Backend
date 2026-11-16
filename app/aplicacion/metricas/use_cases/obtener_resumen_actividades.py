from app.aplicacion.metricas.dto.metricas_dashboard_dto import ResumenActividadesDto
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerResumenActividadesUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> ResumenActividadesDto:
        resumen_raw = self.repositorio.obtener_resumen_actividades(year, mes)
        return ResumenActividadesDto(
            agendadas=resumen_raw["agendadas"],
            concretadas=resumen_raw["concretadas"],
            pendientes=resumen_raw["pendientes"],
            porcentaje_cumplimiento=float(
                resumen_raw["porcentaje_cumplimiento"]
            ),
        )
