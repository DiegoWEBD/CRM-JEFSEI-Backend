from app.aplicacion.metricas.dto.metricas_dashboard_dto import ItemValorDto
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerPrimaPorEjecutivoUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> list[ItemValorDto]:
        por_ejecutivo_raw = self.repositorio.obtener_prima_por_ejecutivo(
            year, mes
        )
        return [
            ItemValorDto(nombre=r["nombre"], valor=float(r["valor"]))
            for r in por_ejecutivo_raw
        ]
