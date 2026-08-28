from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.aplicacion.metricas.dto.kpi_renovacion_dto import KpiRenovacionDto
from app.dominio.metricas.repositorio_kpis_comerciales import RepositorioKpisComerciales


class ObtenerTasaRenovacionUseCase:

    def __init__(self, repositorio: RepositorioKpisComerciales):
        self.repositorio = repositorio

    def ejecutar(self, filtros: FiltrosKpiDto) -> KpiRenovacionDto:
        data = self.repositorio.obtener_tasa_renovacion(filtros)
        return KpiRenovacionDto(
            polizas_vencidas=data['polizas_vencidas'],
            polizas_renovadas=data['polizas_renovadas'],
            tasa_renovacion_pct=data['tasa_renovacion_pct'],
        )
