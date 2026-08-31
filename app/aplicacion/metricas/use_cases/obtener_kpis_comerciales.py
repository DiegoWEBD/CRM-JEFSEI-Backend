from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.aplicacion.metricas.dto.kpis_comerciales_dto import (
    AgingConsolidadoDto,
    CierreConsolidadoDto,
    ConversionConsolidadoDto,
    KpisComercialesDto,
    MorosidadConsolidadoDto,
    PrimaMetaConsolidadoDto,
    PrimaRiesgoConsolidadoDto,
    RenovacionConsolidadoDto,
    TiempoCierreConsolidadoDto,
)
from app.aplicacion.metricas.use_cases.obtener_aging_pipeline import ObtenerAgingPipelineUseCase
from app.aplicacion.metricas.use_cases.obtener_conversion_prospectos import ObtenerConversionProspectosUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_en_riesgo import ObtenerPrimaEnRiesgoUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_vs_meta import ObtenerPrimaVsMetaUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_cierre import ObtenerTasaCierreUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_morosidad import ObtenerTasaMorosidadUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_renovacion import ObtenerTasaRenovacionUseCase
from app.aplicacion.metricas.use_cases.obtener_tiempo_promedio_cierre import ObtenerTiempoPromedioCierreUseCase


class ObtenerKpisComercialesUseCase:

    def __init__(
        self,
        conversion_uc: ObtenerConversionProspectosUseCase,
        cierre_uc: ObtenerTasaCierreUseCase,
        prima_meta_uc: ObtenerPrimaVsMetaUseCase,
        tiempo_cierre_uc: ObtenerTiempoPromedioCierreUseCase,
        aging_uc: ObtenerAgingPipelineUseCase,
        renovacion_uc: ObtenerTasaRenovacionUseCase,
        prima_riesgo_uc: ObtenerPrimaEnRiesgoUseCase,
        morosidad_uc: ObtenerTasaMorosidadUseCase,
    ):
        self.conversion_uc = conversion_uc
        self.cierre_uc = cierre_uc
        self.prima_meta_uc = prima_meta_uc
        self.tiempo_cierre_uc = tiempo_cierre_uc
        self.aging_uc = aging_uc
        self.renovacion_uc = renovacion_uc
        self.prima_riesgo_uc = prima_riesgo_uc
        self.morosidad_uc = morosidad_uc

    def ejecutar(self, filtros: FiltrosKpiDto, dias_ventana: int = 30) -> KpisComercialesDto:
        conversion = self.conversion_uc.ejecutar(filtros)
        cierre = self.cierre_uc.ejecutar(filtros)
        prima_meta_list = self.prima_meta_uc.ejecutar(filtros)
        tiempo_cierre = self.tiempo_cierre_uc.ejecutar(filtros)
        aging = self.aging_uc.ejecutar(filtros)
        renovacion = self.renovacion_uc.ejecutar(filtros)
        prima_riesgo = self.prima_riesgo_uc.ejecutar(filtros, dias_ventana)
        morosidad = self.morosidad_uc.ejecutar(filtros)

        total_prima = sum(e.prima_neta_uf for e in prima_meta_list)
        total_meta = sum(e.meta_mensual_uf for e in prima_meta_list if e.meta_mensual_uf is not None)
        cumplimiento = round(total_prima * 100.0 / total_meta, 2) if total_meta > 0 else 0.0

        return KpisComercialesDto(
            conversion_prospectos=ConversionConsolidadoDto(
                total_prospectos=conversion.total_prospectos,
                prospectos_convertidos=conversion.prospectos_convertidos,
                tasa_pct=conversion.tasa_conversion_pct,
            ),
            cierre_oportunidades=CierreConsolidadoDto(
                procesos_cerrados=cierre.total_procesos_cerrados,
                procesos_ganados=cierre.procesos_ganados,
                procesos_perdidos=cierre.procesos_perdidos,
                tasa_pct=cierre.tasa_cierre_pct,
            ),
            prima_vs_meta=PrimaMetaConsolidadoDto(
                prima_neta_uf=total_prima,
                meta_uf=total_meta,
                cumplimiento_pct=cumplimiento,
            ),
            tiempo_promedio_cierre=TiempoCierreConsolidadoDto(
                promedio_dias=tiempo_cierre.tiempo_promedio_dias,
            ),
            aging_pipeline=AgingConsolidadoDto(
                total_abiertos=aging.total_abiertos,
                rangos=aging.rangos,
            ),
            renovacion=RenovacionConsolidadoDto(
                polizas_vencidas=renovacion.polizas_vencidas,
                polizas_renovadas=renovacion.polizas_renovadas,
                tasa_pct=renovacion.tasa_renovacion_pct,
            ),
            prima_en_riesgo=PrimaRiesgoConsolidadoDto(
                polizas=prima_riesgo.polizas_en_riesgo,
                prima_uf=prima_riesgo.prima_en_riesgo_uf,
            ),
            morosidad=MorosidadConsolidadoDto(
                total_cuotas=morosidad.total_cuotas,
                cuotas_morosas=morosidad.cuotas_morosas,
                tasa_pct=morosidad.tasa_morosidad_pct,
            ),
        )
