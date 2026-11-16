from app.aplicacion.metricas.dto.metricas_dashboard_dto import ItemCantidadDto
from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)


class ObtenerPolizasPorRamoUseCase:

    def __init__(
        self,
        repositorio: RepositorioMetricasDashboard,
    ):
        self.repositorio = repositorio

    def ejecutar(self, year: int, mes: int) -> list[ItemCantidadDto]:
        por_ramo_raw = self.repositorio.obtener_polizas_por_producto(year, mes)
        return [
            ItemCantidadDto(nombre=r["nombre"], cantidad=r["cantidad"])
            for r in por_ramo_raw
        ]
