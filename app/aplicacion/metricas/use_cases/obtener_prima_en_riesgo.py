from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.aplicacion.metricas.dto.kpi_prima_riesgo_dto import KpiPrimaRiesgoDto
from app.dominio.metricas.repositorio_kpis_comerciales import RepositorioKpisComerciales


class ObtenerPrimaEnRiesgoUseCase:

    def __init__(self, repositorio: RepositorioKpisComerciales):
        self.repositorio = repositorio

    def ejecutar(self, filtros: FiltrosKpiDto, dias_ventana: int = 30) -> KpiPrimaRiesgoDto:
        data = self.repositorio.obtener_prima_en_riesgo(filtros, dias_ventana)
        return KpiPrimaRiesgoDto(
            prima_en_riesgo_uf=data['prima_en_riesgo_uf'],
            polizas_en_riesgo=data['polizas_en_riesgo'],
        )
