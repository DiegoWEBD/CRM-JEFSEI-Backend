from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.aplicacion.metricas.periodo import resolver_periodo
from app.aplicacion.metricas.use_cases.obtener_actividades_por_tipo import ObtenerActividadesPorTipoUseCase
from app.aplicacion.metricas.use_cases.obtener_comision_mensual import ObtenerComisionMensualUseCase
from app.aplicacion.metricas.use_cases.obtener_compania_top import ObtenerCompaniaTopUseCase
from app.aplicacion.metricas.use_cases.obtener_polizas_por_comuna import ObtenerPolizasPorComunaUseCase
from app.aplicacion.metricas.use_cases.obtener_polizas_por_ramo import ObtenerPolizasPorRamoUseCase
from app.aplicacion.metricas.use_cases.obtener_polizas_por_rango_edad import ObtenerPolizasPorRangoEdadUseCase
from app.aplicacion.metricas.use_cases.obtener_polizas_por_sexo import ObtenerPolizasPorSexoUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_cotizada import ObtenerPrimaCotizadaUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_esperada import ObtenerPrimaEsperadaUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_neta_mensual import ObtenerPrimaNetaMensualUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_por_compania import ObtenerPrimaPorCompaniaUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_por_ejecutivo import ObtenerPrimaPorEjecutivoUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_por_ramo import ObtenerPrimaPorRamoUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_potencial_estimada import ObtenerPrimaPotencialEstimadaUseCase
from app.aplicacion.metricas.use_cases.obtener_prima_vendida_mensual_ej_comercial import ObtenerPrimaVendidaMensualEjComercialUseCase
from app.aplicacion.metricas.use_cases.obtener_progreso_comision_mensual_ej_comercial import ObtenerProgresoComisionMensualEjComercialUseCase
from app.aplicacion.metricas.use_cases.obtener_proyeccion_prima_esperada import ObtenerProyeccionPrimaEsperadaUseCase
from app.aplicacion.metricas.use_cases.obtener_resumen_actividades import ObtenerResumenActividadesUseCase
from app.aplicacion.metricas.use_cases.obtener_tasa_cierre import ObtenerTasaCierreUseCase
from app.aplicacion.metricas.use_cases.obtener_tendencia_anual import ObtenerTendenciaAnualUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.metricas.dependencias.deps import (
    get_obtener_actividades_por_tipo_use_case,
    get_obtener_comision_mensual_use_case,
    get_obtener_compania_top_use_case,
    get_obtener_polizas_por_comuna_use_case,
    get_obtener_polizas_por_ramo_use_case,
    get_obtener_polizas_por_rango_edad_use_case,
    get_obtener_polizas_por_sexo_use_case,
    get_obtener_prima_cotizada_use_case,
    get_obtener_prima_esperada_use_case,
    get_obtener_prima_neta_mensual_use_case,
    get_obtener_prima_por_compania_use_case,
    get_obtener_prima_por_ejecutivo_use_case,
    get_obtener_prima_por_ramo_use_case,
    get_obtener_prima_potencial_estimada_use_case,
    get_obtener_prima_vendida_mensual_ej_comercial_use_case,
    get_obtener_progreso_comision_mensual_ej_comercial_use_case,
    get_obtener_proyeccion_prima_esperada_use_case,
    get_obtener_resumen_actividades_use_case,
    get_obtener_tasa_cierre_use_case,
    get_obtener_tendencia_anual_use_case,
)


router = APIRouter(prefix='/metricas', tags=['Metricas'])


@router.get('/prima-neta-mensual', status_code=status.HTTP_200_OK)
def obtener_prima_neta_mensual(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPrimaNetaMensualUseCase = Depends(
        get_obtener_prima_neta_mensual_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/comision-mensual', status_code=status.HTTP_200_OK)
def obtener_comision_mensual(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerComisionMensualUseCase = Depends(
        get_obtener_comision_mensual_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/tendencia-anual', status_code=status.HTTP_200_OK)
def obtener_tendencia_anual(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerTendenciaAnualUseCase = Depends(
        get_obtener_tendencia_anual_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/prima-por-compania', status_code=status.HTTP_200_OK)
def obtener_prima_por_compania(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPrimaPorCompaniaUseCase = Depends(
        get_obtener_prima_por_compania_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/compania-top', status_code=status.HTTP_200_OK)
def obtener_compania_top(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerCompaniaTopUseCase = Depends(
        get_obtener_compania_top_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/prima-por-ejecutivo', status_code=status.HTTP_200_OK)
def obtener_prima_por_ejecutivo(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPrimaPorEjecutivoUseCase = Depends(
        get_obtener_prima_por_ejecutivo_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/prima-por-ramo', status_code=status.HTTP_200_OK)
def obtener_prima_por_ramo(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPrimaPorRamoUseCase = Depends(
        get_obtener_prima_por_ramo_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/actividades-por-tipo', status_code=status.HTTP_200_OK)
def obtener_actividades_por_tipo(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerActividadesPorTipoUseCase = Depends(
        get_obtener_actividades_por_tipo_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/resumen-actividades', status_code=status.HTTP_200_OK)
def obtener_resumen_actividades(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerResumenActividadesUseCase = Depends(
        get_obtener_resumen_actividades_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/polizas-por-comuna', status_code=status.HTTP_200_OK)
def obtener_polizas_por_comuna(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPolizasPorComunaUseCase = Depends(
        get_obtener_polizas_por_comuna_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/polizas-por-sexo', status_code=status.HTTP_200_OK)
def obtener_polizas_por_sexo(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPolizasPorSexoUseCase = Depends(
        get_obtener_polizas_por_sexo_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/polizas-por-rango-edad', status_code=status.HTTP_200_OK)
def obtener_polizas_por_rango_edad(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPolizasPorRangoEdadUseCase = Depends(
        get_obtener_polizas_por_rango_edad_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/polizas-por-ramo', status_code=status.HTTP_200_OK)
def obtener_polizas_por_ramo(
    mes: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPolizasPorRamoUseCase = Depends(
        get_obtener_polizas_por_ramo_use_case
    ),
):
    anio, mes_val = resolver_periodo(mes, year)
    return use_case.ejecutar(anio, mes_val)


@router.get('/prima-cotizada', status_code=status.HTTP_200_OK)
def obtener_prima_cotizada(
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPrimaCotizadaUseCase = Depends(
        get_obtener_prima_cotizada_use_case
    ),
):
    return use_case.ejecutar()


@router.get('/prima-potencial-estimada', status_code=status.HTTP_200_OK)
def obtener_prima_potencial_estimada(
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPrimaPotencialEstimadaUseCase = Depends(
        get_obtener_prima_potencial_estimada_use_case
    ),
):
    return use_case.ejecutar()


@router.get('/prima-esperada', status_code=status.HTTP_200_OK)
def obtener_prima_esperada(
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerPrimaEsperadaUseCase = Depends(
        get_obtener_prima_esperada_use_case
    ),
):
    return use_case.ejecutar()


@router.get('/proyeccion-prima-esperada', status_code=status.HTTP_200_OK)
def obtener_proyeccion_prima_esperada(
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerProyeccionPrimaEsperadaUseCase = Depends(
        get_obtener_proyeccion_prima_esperada_use_case
    ),
):
    return use_case.ejecutar()


@router.get('/tasa-cierre', status_code=status.HTTP_200_OK)
def obtener_tasa_cierre(
    _ = Depends(permisos_requeridos('VER_METRICAS_GERENCIA')),
    use_case: ObtenerTasaCierreUseCase = Depends(get_obtener_tasa_cierre_use_case),
):
    return use_case.ejecutar()


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
