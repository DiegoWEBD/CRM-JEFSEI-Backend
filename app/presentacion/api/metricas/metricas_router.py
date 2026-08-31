from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
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
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.metricas.dependencias.deps import (
    get_obtener_aging_pipeline_use_case,
    get_obtener_conversion_prospectos_use_case,
    get_obtener_kpis_comerciales_use_case,
    get_obtener_metricas_dashboard_gerente_use_case,
    get_obtener_prima_en_riesgo_use_case,
    get_obtener_prima_vendida_mensual_ej_comercial_use_case,
    get_obtener_prima_vs_meta_use_case,
    get_obtener_progreso_comision_mensual_ej_comercial_use_case,
    get_obtener_tasa_cierre_use_case,
    get_obtener_tasa_morosidad_use_case,
    get_obtener_tasa_renovacion_use_case,
    get_obtener_tiempo_promedio_cierre_use_case,
)


router = APIRouter(prefix='/metricas', tags=['Metricas'])


def _build_filtros(
    usuario: Usuario,
    year: int | None,
    month: int | None,
    rut_ejecutivo: str | None,
    id_linea_negocio: int | None,
    id_producto: int | None,
    id_sucursal: int | None,
) -> FiltrosKpiDto:
    tiene_global = any(
        p.codigo in ('VER_METRICAS_GERENCIA',)
        for r in usuario.roles
        for p in r.permisos
    )
    rut_final = rut_ejecutivo if tiene_global else usuario.rut
    return FiltrosKpiDto(
        year=year,
        month=month,
        rut_ejecutivo=rut_final,
        id_linea_negocio=id_linea_negocio,
        id_producto=id_producto,
        id_sucursal=id_sucursal,
    )


@router.get('/dashboard-gerente', status_code=status.HTTP_200_OK)
def obtener_metricas_dashboard_gerente(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerMetricasDashboardGerenteUseCase = Depends(
        get_obtener_metricas_dashboard_gerente_use_case
    ),
):
    return use_case.ejecutar(mes=mes, year=year)


@router.get('/ejecutivos-comerciales', status_code=status.HTTP_200_OK)
def obtener_usuarios(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_EJECUTIVO')),
    obtener_prima_vendida_use_case: ObtenerPrimaVendidaMensualEjComercialUseCase = Depends(get_obtener_prima_vendida_mensual_ej_comercial_use_case),
    obtener_progreso_comision_use_case: ObtenerProgresoComisionMensualEjComercialUseCase = Depends(get_obtener_progreso_comision_mensual_ej_comercial_use_case)
):
    try:
        prima_vendida = obtener_prima_vendida_use_case.ejecutar(usuario.rut)
        comision = obtener_progreso_comision_use_case.ejecutar(usuario)

        return {
            'prima_vendida': prima_vendida,
            'meta_mensual': usuario.meta_mensual_uf,
            'comision': comision
        }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )


@router.get('/conversion-prospectos', status_code=status.HTTP_200_OK)
def obtener_conversion_prospectos(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_GERENCIA', 'VER_METRICAS_EJECUTIVO')),
    year: int | None = Query(None, ge=2000),
    month: int | None = Query(None, ge=1, le=12),
    rut_ejecutivo: str | None = Query(None),
    id_linea_negocio: int | None = Query(None),
    id_producto: int | None = Query(None),
    id_sucursal: int | None = Query(None),
    use_case: ObtenerConversionProspectosUseCase = Depends(get_obtener_conversion_prospectos_use_case),
):
    filtros = _build_filtros(usuario, year, month, rut_ejecutivo, id_linea_negocio, id_producto, id_sucursal)
    return use_case.ejecutar(filtros)


@router.get('/tasa-cierre', status_code=status.HTTP_200_OK)
def obtener_tasa_cierre(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_GERENCIA', 'VER_METRICAS_EJECUTIVO')),
    year: int | None = Query(None, ge=2000),
    month: int | None = Query(None, ge=1, le=12),
    rut_ejecutivo: str | None = Query(None),
    id_linea_negocio: int | None = Query(None),
    id_producto: int | None = Query(None),
    id_sucursal: int | None = Query(None),
    use_case: ObtenerTasaCierreUseCase = Depends(get_obtener_tasa_cierre_use_case),
):
    filtros = _build_filtros(usuario, year, month, rut_ejecutivo, id_linea_negocio, id_producto, id_sucursal)
    return use_case.ejecutar(filtros)


@router.get('/prima-vs-meta', status_code=status.HTTP_200_OK)
def obtener_prima_vs_meta(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_GERENCIA', 'VER_METRICAS_EJECUTIVO')),
    year: int | None = Query(None, ge=2000),
    month: int | None = Query(None, ge=1, le=12),
    rut_ejecutivo: str | None = Query(None),
    id_linea_negocio: int | None = Query(None),
    id_producto: int | None = Query(None),
    id_sucursal: int | None = Query(None),
    use_case: ObtenerPrimaVsMetaUseCase = Depends(get_obtener_prima_vs_meta_use_case),
):
    filtros = _build_filtros(usuario, year, month, rut_ejecutivo, id_linea_negocio, id_producto, id_sucursal)
    return use_case.ejecutar(filtros)


@router.get('/tiempo-promedio-cierre', status_code=status.HTTP_200_OK)
def obtener_tiempo_promedio_cierre(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_GERENCIA', 'VER_METRICAS_EJECUTIVO')),
    year: int | None = Query(None, ge=2000),
    month: int | None = Query(None, ge=1, le=12),
    rut_ejecutivo: str | None = Query(None),
    id_linea_negocio: int | None = Query(None),
    id_producto: int | None = Query(None),
    id_sucursal: int | None = Query(None),
    use_case: ObtenerTiempoPromedioCierreUseCase = Depends(get_obtener_tiempo_promedio_cierre_use_case),
):
    filtros = _build_filtros(usuario, year, month, rut_ejecutivo, id_linea_negocio, id_producto, id_sucursal)
    return use_case.ejecutar(filtros)


@router.get('/aging-pipeline', status_code=status.HTTP_200_OK)
def obtener_aging_pipeline(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_GERENCIA', 'VER_METRICAS_EJECUTIVO')),
    year: int | None = Query(None, ge=2000),
    month: int | None = Query(None, ge=1, le=12),
    rut_ejecutivo: str | None = Query(None),
    id_linea_negocio: int | None = Query(None),
    id_producto: int | None = Query(None),
    id_sucursal: int | None = Query(None),
    use_case: ObtenerAgingPipelineUseCase = Depends(get_obtener_aging_pipeline_use_case),
):
    filtros = _build_filtros(usuario, year, month, rut_ejecutivo, id_linea_negocio, id_producto, id_sucursal)
    return use_case.ejecutar(filtros)


@router.get('/tasa-renovacion', status_code=status.HTTP_200_OK)
def obtener_tasa_renovacion(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_GERENCIA', 'VER_METRICAS_EJECUTIVO')),
    year: int | None = Query(None, ge=2000),
    month: int | None = Query(None, ge=1, le=12),
    rut_ejecutivo: str | None = Query(None),
    id_linea_negocio: int | None = Query(None),
    id_producto: int | None = Query(None),
    id_sucursal: int | None = Query(None),
    use_case: ObtenerTasaRenovacionUseCase = Depends(get_obtener_tasa_renovacion_use_case),
):
    filtros = _build_filtros(usuario, year, month, rut_ejecutivo, id_linea_negocio, id_producto, id_sucursal)
    return use_case.ejecutar(filtros)


@router.get('/prima-en-riesgo', status_code=status.HTTP_200_OK)
def obtener_prima_en_riesgo(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_GERENCIA', 'VER_METRICAS_EJECUTIVO')),
    year: int | None = Query(None, ge=2000),
    month: int | None = Query(None, ge=1, le=12),
    rut_ejecutivo: str | None = Query(None),
    id_linea_negocio: int | None = Query(None),
    id_producto: int | None = Query(None),
    id_sucursal: int | None = Query(None),
    dias_ventana: int = Query(30, ge=1),
    use_case: ObtenerPrimaEnRiesgoUseCase = Depends(get_obtener_prima_en_riesgo_use_case),
):
    filtros = _build_filtros(usuario, year, month, rut_ejecutivo, id_linea_negocio, id_producto, id_sucursal)
    return use_case.ejecutar(filtros, dias_ventana)


@router.get('/tasa-morosidad', status_code=status.HTTP_200_OK)
def obtener_tasa_morosidad(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_GERENCIA', 'VER_METRICAS_EJECUTIVO')),
    year: int | None = Query(None, ge=2000),
    month: int | None = Query(None, ge=1, le=12),
    rut_ejecutivo: str | None = Query(None),
    id_linea_negocio: int | None = Query(None),
    id_producto: int | None = Query(None),
    id_sucursal: int | None = Query(None),
    use_case: ObtenerTasaMorosidadUseCase = Depends(get_obtener_tasa_morosidad_use_case),
):
    filtros = _build_filtros(usuario, year, month, rut_ejecutivo, id_linea_negocio, id_producto, id_sucursal)
    return use_case.ejecutar(filtros)


@router.get('/kpis-comerciales', status_code=status.HTTP_200_OK)
def obtener_kpis_comerciales(
    usuario: Usuario = Depends(permisos_requeridos('VER_METRICAS_GERENCIA', 'VER_METRICAS_EJECUTIVO')),
    year: int | None = Query(None, ge=2000),
    month: int | None = Query(None, ge=1, le=12),
    rut_ejecutivo: str | None = Query(None),
    id_linea_negocio: int | None = Query(None),
    id_producto: int | None = Query(None),
    id_sucursal: int | None = Query(None),
    dias_ventana: int = Query(30, ge=1),
    use_case: ObtenerKpisComercialesUseCase = Depends(get_obtener_kpis_comerciales_use_case),
):
    filtros = _build_filtros(usuario, year, month, rut_ejecutivo, id_linea_negocio, id_producto, id_sucursal)
    return use_case.ejecutar(filtros, dias_ventana)
