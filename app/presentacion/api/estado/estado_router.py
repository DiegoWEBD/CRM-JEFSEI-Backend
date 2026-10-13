from fastapi import APIRouter, Depends, status

from app.aplicacion.estado.use_cases.actualizar_estado_configuracion import ActualizarEstadoConfiguracionUseCase
from app.aplicacion.estado.use_cases.actualizar_transicion import ActualizarTransicionUseCase
from app.aplicacion.estado.use_cases.crear_transicion import CrearTransicionUseCase
from app.aplicacion.estado.use_cases.eliminar_transicion import EliminarTransicionUseCase
from app.aplicacion.estado.use_cases.obtener_estados_configuracion import ObtenerEstadosConfiguracionUseCase
from app.aplicacion.estado.use_cases.obtener_transiciones_admin import ObtenerTransicionesAdminUseCase
from app.aplicacion.estado.use_cases.obtener_transiciones_manuales import ObtenerTransicionesManualesUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.estado.dependencias.deps import (
    get_actualizar_estado_configuracion_use_case,
    get_actualizar_transicion_use_case,
    get_crear_transicion_use_case,
    get_eliminar_transicion_use_case,
    get_obtener_estados_configuracion_use_case,
    get_obtener_transiciones_admin_use_case,
    get_obtener_transiciones_manuales_use_case,
)
from app.presentacion.api.estado.dto.actualizar_estado_configuracion_request import ActualizarEstadoConfiguracionRequest
from app.presentacion.api.estado.dto.actualizar_transicion_request import ActualizarTransicionRequest
from app.presentacion.api.estado.dto.crear_transicion_request import CrearTransicionRequest
from app.presentacion.api.estado.mappers.etapa_configuracion_mapper import EtapaConfiguracionMapper
from app.presentacion.api.estado.mappers.transicion_admin_mapper import TransicionAdminMapper
from app.presentacion.api.estado.mappers.transicion_manual_mapper import TransicionManualMapper

router = APIRouter(prefix='/estados', tags=['Estados'])

ADMINISTRAR_ESTADOS = 'ADMINISTRAR_ESTADOS_PROCESO_COMERCIAL'


@router.get('/{codigo_estado}/transiciones-manuales', status_code=status.HTTP_200_OK)
def obtener_transiciones_manuales(
    codigo_estado: str,
    _: Usuario = Depends(permisos_requeridos('ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS')),
    use_case: ObtenerTransicionesManualesUseCase = Depends(get_obtener_transiciones_manuales_use_case)
):
    transiciones = use_case.ejecutar(codigo_estado)

    return {
        'transiciones': TransicionManualMapper(transiciones).map()
    }


@router.get('/configuracion', status_code=status.HTTP_200_OK)
def obtener_estados_configuracion(
    _ = Depends(permisos_requeridos(ADMINISTRAR_ESTADOS)),
    use_case: ObtenerEstadosConfiguracionUseCase = Depends(get_obtener_estados_configuracion_use_case)
):
    estados = use_case.ejecutar()

    return {
        'data': EtapaConfiguracionMapper(estados).map()
    }


@router.patch('/{codigo_estado}/configuracion', status_code=status.HTTP_200_OK)
def actualizar_estado_configuracion(
    codigo_estado: str,
    request: ActualizarEstadoConfiguracionRequest,
    _ = Depends(permisos_requeridos(ADMINISTRAR_ESTADOS)),
    use_case: ActualizarEstadoConfiguracionUseCase = Depends(get_actualizar_estado_configuracion_use_case)
):
    actualizado = use_case.ejecutar(
        codigo=codigo_estado,
        probabilidad_cierre=request.probabilidad_cierre,
    )

    if not actualizado:
        return {'message': 'No se pudo actualizar la configuración del estado'}

    return {
        'message': 'Configuración del estado actualizada correctamente'
    }


@router.get('/{codigo_estado}/transiciones', status_code=status.HTTP_200_OK)
def obtener_transiciones_admin(
    codigo_estado: str,
    _ = Depends(permisos_requeridos(ADMINISTRAR_ESTADOS)),
    use_case: ObtenerTransicionesAdminUseCase = Depends(get_obtener_transiciones_admin_use_case)
):
    transiciones = use_case.ejecutar(codigo_estado)

    return {
        'data': TransicionAdminMapper(transiciones).map()
    }


@router.post('/{codigo_estado}/transiciones', status_code=status.HTTP_201_CREATED)
def crear_transicion(
    codigo_estado: str,
    request: CrearTransicionRequest,
    _ = Depends(permisos_requeridos(ADMINISTRAR_ESTADOS)),
    use_case: CrearTransicionUseCase = Depends(get_crear_transicion_use_case)
):
    registrado = use_case.ejecutar(
        codigo_estado_origen=codigo_estado,
        codigo_estado_destino=request.codigo_estado_destino,
        es_manual=request.es_manual,
        es_principal=request.es_principal,
        accion_requerida=request.accion_requerida,
    )

    if not registrado:
        return {'message': 'No se pudo registrar la transición'}

    return {
        'message': 'Transición registrada correctamente'
    }


@router.put('/{codigo_estado}/transiciones/{codigo_estado_destino}', status_code=status.HTTP_200_OK)
def actualizar_transicion(
    codigo_estado: str,
    codigo_estado_destino: str,
    request: ActualizarTransicionRequest,
    _ = Depends(permisos_requeridos(ADMINISTRAR_ESTADOS)),
    use_case: ActualizarTransicionUseCase = Depends(get_actualizar_transicion_use_case)
):
    actualizado = use_case.ejecutar(
        codigo_estado_origen=codigo_estado,
        codigo_estado_destino=codigo_estado_destino,
        es_manual=request.es_manual,
        accion_requerida=request.accion_requerida,
        dias_limite=request.dias_limite,
    )

    if not actualizado:
        return {'message': 'No se pudo actualizar la transición'}

    return {
        'message': 'Transición actualizada correctamente'
    }


@router.delete('/{codigo_estado}/transiciones/{codigo_estado_destino}', status_code=status.HTTP_200_OK)
def eliminar_transicion(
    codigo_estado: str,
    codigo_estado_destino: str,
    _ = Depends(permisos_requeridos(ADMINISTRAR_ESTADOS)),
    use_case: EliminarTransicionUseCase = Depends(get_eliminar_transicion_use_case)
):
    eliminado = use_case.ejecutar(
        codigo_estado_origen=codigo_estado,
        codigo_estado_destino=codigo_estado_destino,
    )

    if not eliminado:
        return {'message': 'No se pudo eliminar la transición'}

    return {
        'message': 'Transición eliminada correctamente'
    }
