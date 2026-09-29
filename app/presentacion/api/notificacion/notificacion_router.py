import math
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.aplicacion.notificacion.use_cases.marcar_notificacion_leida import MarcarNotificacionLeidaUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificaciones_leidas import MarcarNotificacionesLeidasUseCase
from app.aplicacion.notificacion.use_cases.obtener_contador_no_leidas import ObtenerContadorNoLeidasUseCase
from app.aplicacion.notificacion.use_cases.obtener_notificaciones import ObtenerNotificacionesUseCase
from app.aplicacion.notificacion.use_cases.obtener_oportunidades_en_riesgo import ObtenerOportunidadesEnRiesgoUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.dto.deps import get_paginacion_params
from app.presentacion.api.dto.paginacion_params import PaginacionParams
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from app.presentacion.api.notificacion.dependencias.deps import (
    get_marcar_notificacion_leida_use_case,
    get_marcar_notificaciones_leidas_use_case,
    get_obtener_contador_no_leidas_use_case,
    get_obtener_notificaciones_use_case,
    get_obtener_oportunidades_en_riesgo_use_case,
)


router = APIRouter(prefix='/notificaciones', tags=['Notificaciones'])

NIVELES_VALIDOS = {'INFO', 'AVISO', 'CRITICO'}


def _validar_nivel(nivel: str | None) -> None:
    if nivel and nivel not in NIVELES_VALIDOS:
        raise BadRequestException(f'Nivel inválido: "{nivel}". Debe ser uno de: INFO, AVISO, CRITICO')


@router.get('/', status_code=status.HTTP_200_OK)
def obtener_notificaciones(
    no_leidas: Optional[bool] = Query(None),
    nivel: Optional[str] = Query(None),
    codigo_tipo: Optional[str] = Query(None),
    paginacion: PaginacionParams = Depends(get_paginacion_params),
    usuario: Usuario = Depends(permisos_requeridos('VER_ALERTAS')),
    use_case: ObtenerNotificacionesUseCase = Depends(get_obtener_notificaciones_use_case)
):
    _validar_nivel(nivel)

    datos, total = use_case.ejecutar_paginado(
        rut_usuario=usuario.rut,
        pagina=paginacion.pagina,
        tamano_pagina=paginacion.tamano_pagina,
        no_leidas=no_leidas,
        nivel=nivel,
        codigo_tipo=codigo_tipo,
    )
    total_paginas = math.ceil(total / paginacion.tamano_pagina) if total > 0 else 1

    return {
        'data': datos,
        'total': total,
        'pagina': paginacion.pagina,
        'tamano_pagina': paginacion.tamano_pagina,
        'total_paginas': total_paginas,
    }


@router.get('/contador', status_code=status.HTTP_200_OK)
def obtener_contador_no_leidas(
    usuario: Usuario = Depends(permisos_requeridos('VER_ALERTAS')),
    use_case: ObtenerContadorNoLeidasUseCase = Depends(get_obtener_contador_no_leidas_use_case)
):
    contador = use_case.ejecutar(rut_usuario=usuario.rut)

    return {'contador': contador}


@router.get('/oportunidades/en-riesgo', status_code=status.HTTP_200_OK)
def obtener_oportunidades_en_riesgo(
    paginacion: PaginacionParams = Depends(get_paginacion_params),
    usuario: Usuario = Depends(permisos_requeridos('VER_ALERTAS')),
    use_case: ObtenerOportunidadesEnRiesgoUseCase = Depends(get_obtener_oportunidades_en_riesgo_use_case)
):
    datos, total = use_case.ejecutar_paginado(
        rut_usuario=usuario.rut,
        pagina=paginacion.pagina,
        tamano_pagina=paginacion.tamano_pagina,
    )
    total_paginas = math.ceil(total / paginacion.tamano_pagina) if total > 0 else 1

    return {
        'data': datos,
        'total': total,
        'pagina': paginacion.pagina,
        'tamano_pagina': paginacion.tamano_pagina,
        'total_paginas': total_paginas,
    }


@router.patch('/{id}/leer', status_code=status.HTTP_200_OK)
def marcar_notificacion_leida(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('VER_ALERTAS')),
    use_case: MarcarNotificacionLeidaUseCase = Depends(get_marcar_notificacion_leida_use_case)
):
    use_case.ejecutar(id_notificacion=id, rut_usuario=usuario.rut)

    return {'message': 'Notificación marcada como leída'}


@router.post('/leer-todas', status_code=status.HTTP_200_OK)
def marcar_notificaciones_leidas(
    usuario: Usuario = Depends(permisos_requeridos('VER_ALERTAS')),
    use_case: MarcarNotificacionesLeidasUseCase = Depends(get_marcar_notificaciones_leidas_use_case)
):
    total = use_case.ejecutar(rut_usuario=usuario.rut)

    return {'message': 'Notificaciones marcadas como leídas', 'total': total}
