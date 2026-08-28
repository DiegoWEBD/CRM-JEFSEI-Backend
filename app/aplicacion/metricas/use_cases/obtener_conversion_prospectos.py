from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.aplicacion.metricas.dto.kpi_conversion_dto import KpiConversionDto
from app.dominio.metricas.repositorio_kpis_comerciales import RepositorioKpisComerciales


class ObtenerConversionProspectosUseCase:

    def __init__(self, repositorio: RepositorioKpisComerciales):
        self.repositorio = repositorio

    def ejecutar(self, filtros: FiltrosKpiDto) -> KpiConversionDto:
        data = self.repositorio.obtener_conversion_prospectos(filtros)
        return KpiConversionDto(
            total_prospectos=data['total_prospectos'],
            prospectos_convertidos=data['prospectos_convertidos'],
            tasa_conversion_pct=data['tasa_conversion_pct'],
        )
