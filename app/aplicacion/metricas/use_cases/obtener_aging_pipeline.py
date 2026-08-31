from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.aplicacion.metricas.dto.kpi_aging_dto import AgingRangoDto, KpiAgingDto
from app.dominio.metricas.repositorio_kpis_comerciales import RepositorioKpisComerciales


class ObtenerAgingPipelineUseCase:

    def __init__(self, repositorio: RepositorioKpisComerciales):
        self.repositorio = repositorio

    def ejecutar(self, filtros: FiltrosKpiDto) -> KpiAgingDto:
        data = self.repositorio.obtener_aging_pipeline(filtros)
        rangos = [
            AgingRangoDto(
                rango=r['rango'],
                cantidad=r['cantidad'],
                porcentaje=r['porcentaje'],
            )
            for r in data['rangos']
        ]
        return KpiAgingDto(
            total_abiertos=data['total_abiertos'],
            rangos=rangos,
        )
