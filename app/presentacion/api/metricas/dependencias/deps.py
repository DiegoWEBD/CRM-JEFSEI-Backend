from app.aplicacion.metricas.use_cases.obtener_aging_pipeline import ObtenerAgingPipelineUseCase
from app.aplicacion.metricas.use_cases.obtener_conversion_prospectos import ObtenerConversionProspectosUseCase
from app.aplicacion.metricas.use_cases.obtener_kpis_comerciales import ObtenerKpisComercialesUseCase
from app.aplicacion.metricas.use_cases.obtener_metricas_dashboard_gerente import ObtenerMetricasDashboardGerenteUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_en_riesgo import ObtenerPrimaEnRiesgoUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_vendida_mensual_ej_comercial import ObtenerPrimaVendidaMensualEjComercialUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_vs_meta import ObtenerPrimaVsMetaUseCase
from app.aplicacion.metricas.use_cases.obtener_progreso_comision_mensual_ej_comercial import ObtenerProgresoComisionMensualEjComercialUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_cierre import ObtenerTasaCierreUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_morosidad import ObtenerTasaMorosidadUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_renovacion import ObtenerTasaRenovacionUseCase
from app.aplicacion.metricas.use_cases.obtener_tiempo_promedio_cierre import ObtenerTiempoPromedioCierreUseCase
from app.infraestructura.metricas.repositorio_kpis_comerciales_postgres import RepositorioKpisComercialesPostgres
from app.infraestructura.metricas.repositorio_metricas_dashboard_postgres import RepositorioMetricasDashboardPostgres
from app.infraestructura.poliza.repositorio_polizas_postgres import RepositorioPolizasPostgres


def get_obtener_prima_vendida_mensual_ej_comercial_use_case():
    repositorio = RepositorioPolizasPostgres()
    return ObtenerPrimaVendidaMensualEjComercialUseCase(repositorio)


def get_obtener_progreso_comision_mensual_ej_comercial_use_case():
    repositorio = RepositorioPolizasPostgres()
    return ObtenerProgresoComisionMensualEjComercialUseCase(repositorio)


def get_obtener_metricas_dashboard_gerente_use_case():
    repositorio = RepositorioMetricasDashboardPostgres()
    return ObtenerMetricasDashboardGerenteUseCase(repositorio)


def _get_repositorio_kpis():
    return RepositorioKpisComercialesPostgres()


def get_obtener_conversion_prospectos_use_case():
    return ObtenerConversionProspectosUseCase(_get_repositorio_kpis())


def get_obtener_tasa_cierre_use_case():
    return ObtenerTasaCierreUseCase(_get_repositorio_kpis())


def get_obtener_prima_vs_meta_use_case():
    return ObtenerPrimaVsMetaUseCase(_get_repositorio_kpis())


def get_obtener_tiempo_promedio_cierre_use_case():
    return ObtenerTiempoPromedioCierreUseCase(_get_repositorio_kpis())


def get_obtener_aging_pipeline_use_case():
    return ObtenerAgingPipelineUseCase(_get_repositorio_kpis())


def get_obtener_tasa_renovacion_use_case():
    return ObtenerTasaRenovacionUseCase(_get_repositorio_kpis())


def get_obtener_prima_en_riesgo_use_case():
    return ObtenerPrimaEnRiesgoUseCase(_get_repositorio_kpis())


def get_obtener_tasa_morosidad_use_case():
    return ObtenerTasaMorosidadUseCase(_get_repositorio_kpis())


def get_obtener_kpis_comerciales_use_case():
    repo = _get_repositorio_kpis()
    return ObtenerKpisComercialesUseCase(
        conversion_uc=ObtenerConversionProspectosUseCase(repo),
        cierre_uc=ObtenerTasaCierreUseCase(repo),
        prima_meta_uc=ObtenerPrimaVsMetaUseCase(repo),
        tiempo_cierre_uc=ObtenerTiempoPromedioCierreUseCase(repo),
        aging_uc=ObtenerAgingPipelineUseCase(repo),
        renovacion_uc=ObtenerTasaRenovacionUseCase(repo),
        prima_riesgo_uc=ObtenerPrimaEnRiesgoUseCase(repo),
        morosidad_uc=ObtenerTasaMorosidadUseCase(repo),
    )