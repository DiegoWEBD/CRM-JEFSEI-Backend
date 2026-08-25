from fastapi import APIRouter, Depends, HTTPException, status

from app.aplicacion.configuracion_condominio.use_cases.eliminar_valor_uf_region import EliminarValorUfRegionUseCase
from app.aplicacion.configuracion_condominio.use_cases.guardar_parametros_depreciacion import GuardarParametrosDepreciacionUseCase
from app.aplicacion.configuracion_condominio.use_cases.guardar_valor_uf_region import GuardarValorUfRegionUseCase
from app.aplicacion.configuracion_condominio.use_cases.obtener_parametros_depreciacion import ObtenerParametrosDepreciacionUseCase
from app.aplicacion.configuracion_condominio.use_cases.obtener_todos_valores_uf_region import ObtenerTodosValoresUfRegionUseCase
from app.aplicacion.configuracion_condominio.use_cases.obtener_valor_uf_region import ObtenerValorUfRegionUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.configuracion_condominio.deps import (
    get_eliminar_valor_uf_region_use_case,
    get_guardar_parametros_depreciacion_use_case,
    get_guardar_valor_uf_region_use_case,
    get_obtener_parametros_depreciacion_use_case,
    get_obtener_todos_valores_uf_region_use_case,
    get_obtener_valor_uf_region_use_case,
)
from app.presentacion.api.configuracion_condominio.dto.guardar_parametros_depreciacion_request import GuardarParametrosDepreciacionRequest
from app.presentacion.api.configuracion_condominio.dto.guardar_valor_uf_region_request import GuardarValorUfRegionRequest
from app.presentacion.api.configuracion_condominio.dto.parametros_depreciacion_json import ParametrosDepreciacionJson
from app.presentacion.api.configuracion_condominio.dto.valor_uf_region_json import ValorUfRegionJson


router = APIRouter(prefix='/configuracion-condominio', tags=['Configuración Condominio'])


@router.get('/valor-uf-region', status_code=status.HTTP_200_OK)
def obtener_todos_valores_uf_region(
    _: Usuario = Depends(permisos_requeridos('ACTUALIZAR_DATOS_PROSPECTO')),
    use_case: ObtenerTodosValoresUfRegionUseCase = Depends(get_obtener_todos_valores_uf_region_use_case)
):
    valores = use_case.ejecutar()
    return {
        'data': [
            ValorUfRegionJson(id=v.id, region=v.region, valor_uf_m2=v.valor_uf_m2).model_dump()
            for v in valores
        ]
    }


@router.get('/valor-uf-region/{region}', status_code=status.HTTP_200_OK)
def obtener_valor_uf_region(
    region: str,
    _: Usuario = Depends(permisos_requeridos('ACTUALIZAR_DATOS_PROSPECTO')),
    use_case: ObtenerValorUfRegionUseCase = Depends(get_obtener_valor_uf_region_use_case)
):
    valor = use_case.ejecutar(region)
    return {
        'valor_uf_m2': valor,
        'disponible': valor is not None
    }


@router.put('/valor-uf-region', status_code=status.HTTP_200_OK)
def guardar_valor_uf_region(
    request: GuardarValorUfRegionRequest,
    _: Usuario = Depends(permisos_requeridos('ADMINISTRAR_CONFIGURACION_CONDOMINIO')),
    use_case: GuardarValorUfRegionUseCase = Depends(get_guardar_valor_uf_region_use_case)
):
    valor = use_case.ejecutar(
        id=request.id,
        region=request.region,
        valor_uf_m2=request.valor_uf_m2
    )
    return {
        'data': ValorUfRegionJson(id=valor.id, region=valor.region, valor_uf_m2=valor.valor_uf_m2).model_dump(),
        'message': 'Valor UF por región guardado correctamente'
    }


@router.delete('/valor-uf-region/{id}', status_code=status.HTTP_200_OK)
def eliminar_valor_uf_region(
    id: int,
    _: Usuario = Depends(permisos_requeridos('ADMINISTRAR_CONFIGURACION_CONDOMINIO')),
    use_case: EliminarValorUfRegionUseCase = Depends(get_eliminar_valor_uf_region_use_case)
):
    use_case.ejecutar(id)
    return {
        'message': 'Valor UF por región eliminado correctamente'
    }


@router.get('/parametros-depreciacion', status_code=status.HTTP_200_OK)
def obtener_parametros_depreciacion(
    _: Usuario = Depends(permisos_requeridos('ACTUALIZAR_DATOS_PROSPECTO')),
    use_case: ObtenerParametrosDepreciacionUseCase = Depends(get_obtener_parametros_depreciacion_use_case)
):
    params = use_case.ejecutar()

    if params is None:
        return {'data': None}

    return {
        'data': ParametrosDepreciacionJson(
            id=params.id,
            antiguedad_sin_depreciacion=params.antiguedad_sin_depreciacion,
            porcentaje_por_anio=params.porcentaje_por_anio,
            antiguedad_maxima=params.antiguedad_maxima,
            porcentaje_maximo=params.porcentaje_maximo
        ).model_dump()
    }


@router.put('/parametros-depreciacion', status_code=status.HTTP_200_OK)
def guardar_parametros_depreciacion(
    request: GuardarParametrosDepreciacionRequest,
    _: Usuario = Depends(permisos_requeridos('ADMINISTRAR_CONFIGURACION_CONDOMINIO')),
    use_case: GuardarParametrosDepreciacionUseCase = Depends(get_guardar_parametros_depreciacion_use_case)
):
    params = use_case.ejecutar(
        id=request.id,
        antiguedad_sin_depreciacion=request.antiguedad_sin_depreciacion,
        porcentaje_por_anio=request.porcentaje_por_anio,
        antiguedad_maxima=request.antiguedad_maxima,
        porcentaje_maximo=request.porcentaje_maximo
    )
    return {
        'data': ParametrosDepreciacionJson(
            id=params.id,
            antiguedad_sin_depreciacion=params.antiguedad_sin_depreciacion,
            porcentaje_por_anio=params.porcentaje_por_anio,
            antiguedad_maxima=params.antiguedad_maxima,
            porcentaje_maximo=params.porcentaje_maximo
        ).model_dump(),
        'message': 'Parámetros de depreciación guardados correctamente'
    }
