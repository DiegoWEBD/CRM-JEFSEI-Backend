from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.aplicacion.metricas.dto.kpi_cierre_dto import KpiCierreDto
from app.dominio.metricas.repositorio_kpis_comerciales import RepositorioKpisComerciales


class ObtenerTasaCierreUseCase:

    def __init__(self, repositorio: RepositorioKpisComerciales):
        self.repositorio = repositorio

    def ejecutar(self, filtros: FiltrosKpiDto) -> KpiCierreDto:
        data = self.repositorio.obtener_tasa_cierre(filtros)
        return KpiCierreDto(
            total_procesos_cerrados=data['total_procesos_cerrados'],
            procesos_ganados=data['procesos_ganados'],
            procesos_perdidos=data['procesos_perdidos'],
            tasa_cierre_pct=data['tasa_cierre_pct'],
            tasa_perdida_pct=data['tasa_perdida_pct'],
        )
