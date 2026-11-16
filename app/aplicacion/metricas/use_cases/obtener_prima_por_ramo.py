from app.aplicacion.metricas.dto.metricas_dashboard_dto import ItemValorDto
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerPrimaPorRamoUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> list[ItemValorDto]:
        por_ramo_raw = self.repositorio.obtener_prima_por_producto(year, mes)
        return [
            ItemValorDto(nombre=r["nombre"], valor=float(r["valor"]))
            for r in por_ramo_raw
        ]
