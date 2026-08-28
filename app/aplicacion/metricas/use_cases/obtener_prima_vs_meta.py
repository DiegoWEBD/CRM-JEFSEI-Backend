from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.aplicacion.metricas.dto.kpi_prima_meta_dto import KpiPrimaMetaEjecutivoDto
from app.dominio.metricas.repositorio_kpis_comerciales import RepositorioKpisComerciales


class ObtenerPrimaVsMetaUseCase:

    def __init__(self, repositorio: RepositorioKpisComerciales):
        self.repositorio = repositorio

    def ejecutar(self, filtros: FiltrosKpiDto) -> list[KpiPrimaMetaEjecutivoDto]:
        rows = self.repositorio.obtener_prima_vs_meta(filtros)
        return [
            KpiPrimaMetaEjecutivoDto(
                rut_ejecutivo=row['rut_ejecutivo'],
                nombre_ejecutivo=row['nombre_ejecutivo'],
                prima_neta_uf=row['prima_neta_uf'],
                meta_mensual_uf=row['meta_mensual_uf'],
                cumplimiento_pct=row['cumplimiento_pct'],
                diferencia_uf=row['diferencia_uf'],
            )
            for row in rows
        ]
