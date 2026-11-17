from app.aplicacion.metricas.use_cases.obtener_actividades_por_tipo import ObtenerActividadesPorTipoUseCase
from app.aplicacion.metricas.use_cases.obtener_aging_pipeline import ObtenerAgingPipelineUseCase
from app.aplicacion.metricas.use_cases.obtener_comision_mensual import ObtenerComisionMensualUseCase
from app.aplicacion.metricas.use_cases.obtener_compania_top import ObtenerCompaniaTopUseCase
from app.aplicacion.metricas.use_cases.obtener_conversion_prospectos import ObtenerConversionProspectosUseCase
from app.aplicacion.metricas.use_cases.obtener_kpis_comerciales import ObtenerKpisComercialesUseCase
from app.aplicacion.metricas.use_cases.obtener_polizas_por_comuna import ObtenerPolizasPorComunaUseCase
from app.aplicacion.metricas.use_cases.obtener_polizas_por_ramo import ObtenerPolizasPorRamoUseCase
from app.aplicacion.metricas.use_cases.obtener_polizas_por_rango_edad import ObtenerPolizasPorRangoEdadUseCase
from app.aplicacion.metricas.use_cases.obtener_polizas_por_sexo import ObtenerPolizasPorSexoUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_cotizada import ObtenerPrimaCotizadaUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_en_riesgo import ObtenerPrimaEnRiesgoUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_esperada import ObtenerPrimaEsperadaUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_neta_mensual import ObtenerPrimaNetaMensualUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_por_compania import ObtenerPrimaPorCompaniaUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_por_ejecutivo import ObtenerPrimaPorEjecutivoUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_por_ramo import ObtenerPrimaPorRamoUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_potencial_estimada import ObtenerPrimaPotencialEstimadaUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_vendida_mensual_ej_comercial import ObtenerPrimaVendidaMensualEjComercialUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_vs_meta import ObtenerPrimaVsMetaUseCase
from app.aplicacion.metricas.use_cases.obtener_progreso_comision_mensual_ej_comercial import ObtenerProgresoComisionMensualEjComercialUseCase
from app.aplicacion.metricas.use_cases.obtener_proyeccion_prima_esperada import ObtenerProyeccionPrimaEsperadaUseCase
from app.aplicacion.metricas.use_cases.obtener_resumen_actividades import ObtenerResumenActividadesUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_cierre import ObtenerTasaCierreUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_morosidad import ObtenerTasaMorosidadUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_renovacion import ObtenerTasaRenovacionUseCase
from app.aplicacion.metricas.use_cases.obtener_tendencia_anual import ObtenerTendenciaAnualUseCase
from app.aplicacion.metricas.use_cases.obtener_tiempo_promedio_cierre import ObtenerTiempoPromedioCierreUseCase
from app.aplicacion.proyeccion.servicios.servicio_proyecciones_comerciales import ServicioProyeccionesComerciales
from app.infraestructura.cotizacion.repositorio_cotizaciones_postgres import RepositorioCotizacionesPostgres
from app.infraestructura.metricas.repositorio_kpis_comerciales_postgres import RepositorioKpisComercialesPostgres
from app.infraestructura.metricas.repositorio_metricas_dashboard_postgres import RepositorioMetricasDashboardPostgres
from app.infraestructura.poliza.repositorio_polizas_postgres import RepositorioPolizasPostgres
from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import RepositorioProcesosComercialesPostgres
from app.infraestructura.solicitud_cotizacion.repositorio_solicitudes_cotizacion_postgres import RepositorioSolicitudesCotizacionPostgres


def get_obtener_prima_vendida_mensual_ej_comercial_use_case():
    repositorio = RepositorioPolizasPostgres()
    return ObtenerPrimaVendidaMensualEjComercialUseCase(repositorio)


def get_obtener_progreso_comision_mensual_ej_comercial_use_case():
    repositorio = RepositorioPolizasPostgres()
    return ObtenerProgresoComisionMensualEjComercialUseCase(repositorio)


def _get_repositorio_dashboard():
    return RepositorioMetricasDashboardPostgres()


def get_obtener_prima_neta_mensual_use_case():
    return ObtenerPrimaNetaMensualUseCase(_get_repositorio_dashboard())


def get_obtener_comision_mensual_use_case():
    return ObtenerComisionMensualUseCase(_get_repositorio_dashboard())


def get_obtener_tendencia_anual_use_case():
    return ObtenerTendenciaAnualUseCase(_get_repositorio_dashboard())


def get_obtener_prima_por_compania_use_case():
    return ObtenerPrimaPorCompaniaUseCase(_get_repositorio_dashboard())


def get_obtener_compania_top_use_case():
    return ObtenerCompaniaTopUseCase(_get_repositorio_dashboard())


def get_obtener_prima_por_ejecutivo_use_case():
    return ObtenerPrimaPorEjecutivoUseCase(_get_repositorio_dashboard())


def get_obtener_prima_por_ramo_use_case():
    return ObtenerPrimaPorRamoUseCase(_get_repositorio_dashboard())


def get_obtener_actividades_por_tipo_use_case():
    return ObtenerActividadesPorTipoUseCase(_get_repositorio_dashboard())


def get_obtener_resumen_actividades_use_case():
    return ObtenerResumenActividadesUseCase(_get_repositorio_dashboard())


def get_obtener_polizas_por_comuna_use_case():
    return ObtenerPolizasPorComunaUseCase(_get_repositorio_dashboard())


def get_obtener_polizas_por_sexo_use_case():
    return ObtenerPolizasPorSexoUseCase()


def get_obtener_polizas_por_rango_edad_use_case():
    return ObtenerPolizasPorRangoEdadUseCase()


def get_obtener_polizas_por_ramo_use_case():
    return ObtenerPolizasPorRamoUseCase(_get_repositorio_dashboard())


def _get_servicio_proyecciones_comerciales():
    return ServicioProyeccionesComerciales(
        repositorio_solicitudes_cotizacion=RepositorioSolicitudesCotizacionPostgres(),
        repositorio_cotizaciones=RepositorioCotizacionesPostgres(),
    )


def _get_obtener_proyecciones_use_case_args():
    return (
        RepositorioProcesosComercialesPostgres(),
        _get_servicio_proyecciones_comerciales(),
    )


def get_obtener_prima_cotizada_use_case():
    return ObtenerPrimaCotizadaUseCase(*_get_obtener_proyecciones_use_case_args())


def get_obtener_prima_potencial_estimada_use_case():
    return ObtenerPrimaPotencialEstimadaUseCase(
        *_get_obtener_proyecciones_use_case_args()
    )


def get_obtener_prima_esperada_use_case():
    return ObtenerPrimaEsperadaUseCase(*_get_obtener_proyecciones_use_case_args())


def get_obtener_proyeccion_prima_esperada_use_case():
    return ObtenerProyeccionPrimaEsperadaUseCase(
        *_get_obtener_proyecciones_use_case_args()
    )


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
