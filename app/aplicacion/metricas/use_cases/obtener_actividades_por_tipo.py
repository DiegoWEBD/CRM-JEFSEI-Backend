from app.aplicacion.metricas.dto.metricas_dashboard_dto import ActividadTipoDto
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerActividadesPorTipoUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> list[ActividadTipoDto]:
        por_tipo_raw = self.repositorio.obtener_actividades_comerciales(
            year, mes
        )
        return [
            ActividadTipoDto(
                tipo=r["tipo"],
                concretadas=r["concretadas"],
                pendientes=r["pendientes"],
            )
            for r in por_tipo_raw
        ]
