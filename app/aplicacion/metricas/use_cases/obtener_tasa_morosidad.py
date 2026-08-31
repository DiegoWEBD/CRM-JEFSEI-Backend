from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.aplicacion.metricas.dto.kpi_morosidad_dto import KpiMorosidadDto
from app.dominio.metricas.repositorio_kpis_comerciales import RepositorioKpisComerciales


class ObtenerTasaMorosidadUseCase:

    def __init__(self, repositorio: RepositorioKpisComerciales):
        self.repositorio = repositorio

    def ejecutar(self, filtros: FiltrosKpiDto) -> KpiMorosidadDto:
        data = self.repositorio.obtener_tasa_morosidad(filtros)
        return KpiMorosidadDto(
            total_cuotas=data['total_cuotas'],
            cuotas_vencidas=data['cuotas_vencidas'],
            cuotas_morosas=data['cuotas_morosas'],
            tasa_morosidad_pct=data['tasa_morosidad_pct'],
        )
