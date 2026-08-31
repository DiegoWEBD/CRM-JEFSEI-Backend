from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.aplicacion.metricas.dto.kpi_tiempo_cierre_dto import KpiTiempoCierreDto
from app.dominio.metricas.repositorio_kpis_comerciales import RepositorioKpisComerciales


class ObtenerTiempoPromedioCierreUseCase:

    def __init__(self, repositorio: RepositorioKpisComerciales):
        self.repositorio = repositorio

    def ejecutar(self, filtros: FiltrosKpiDto) -> KpiTiempoCierreDto:
        data = self.repositorio.obtener_tiempo_promedio_cierre(filtros)
        return KpiTiempoCierreDto(
            procesos_cerrados=data['procesos_cerrados'],
            tiempo_promedio_dias=data['tiempo_promedio_dias'],
            tiempo_minimo_dias=data['tiempo_minimo_dias'],
            tiempo_maximo_dias=data['tiempo_maximo_dias'],
        )
