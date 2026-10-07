import math
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from app.aplicacion.auth.use_cases.obtener_sesiones import ObtenerSesionesUseCase
from app.aplicacion.auth.use_cases.revocar_sesion_admin import RevocarSesionAdminUseCase
from app.aplicacion.auth.use_cases.revocar_todas_sesiones_usuario_admin import (
    RevocarTodasSesionesUsuarioAdminUseCase,
)
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.auditoria.lib.construir_contexto_peticion import construir_contexto_peticion
from app.presentacion.api.dto.deps import get_paginacion_params
from app.presentacion.api.dto.paginacion_params import PaginacionParams
from app.presentacion.api.sesiones.dependencias.deps import (
    get_obtener_sesiones_use_case,
    get_revocar_sesion_admin_use_case,
    get_revocar_todas_sesiones_usuario_admin_use_case,
)
from app.presentacion.api.sesiones.dto.sesion_json import SesionJson
from app.dominio.auth.sesion_con_usuario import SesionConUsuario
from app.presentacion.api.sesiones.lib.parsear_dispositivo import parsear_dispositivo

router = APIRouter(prefix='/sesiones', tags=['Sesiones'])


def _sesion_a_json(sesion: SesionConUsuario) -> SesionJson:
    ahora = datetime.now(timezone.utc)
    esta_activa = sesion.revocado_en is None and sesion.expira_en > ahora

    if esta_activa:
        duracion = (ahora - sesion.creado_en).total_seconds() / 60
    elif sesion.ultimo_acceso is not None:
        duracion = (sesion.ultimo_acceso - sesion.creado_en).total_seconds() / 60
    elif sesion.revocado_en is not None:
        duracion = (sesion.revocado_en - sesion.creado_en).total_seconds() / 60
    else:
        duracion = (sesion.expira_en - sesion.creado_en).total_seconds() / 60

    return SesionJson(
        id=sesion.id,
        rut_usuario=sesion.rut_usuario,
        nombre_usuario=sesion.nombre_usuario,
        ip=sesion.ip,
        user_agent=sesion.user_agent,
        dispositivo=parsear_dispositivo(sesion.user_agent),
        creado_en=sesion.creado_en,
        ultimo_acceso=sesion.ultimo_acceso,
        duracion_minutos=round(duracion, 1),
        esta_activa=esta_activa,
        revocado_en=sesion.revocado_en,
        motivo_revocacion=sesion.motivo_revocacion,
    )


@router.get('/', status_code=status.HTTP_200_OK)
def obtener_sesiones(
    _ = Depends(permisos_requeridos('VER_SESIONES')),
    paginacion: PaginacionParams = Depends(get_paginacion_params),
    rut_usuario: str | None = Query(None),
    estado: str | None = Query(None),
    use_case: ObtenerSesionesUseCase = Depends(get_obtener_sesiones_use_case),
):
    sesiones, total = use_case.ejecutar_paginado(
        texto_busqueda=paginacion.texto_busqueda,
        rut_usuario=rut_usuario,
        estado=estado,
        pagina=paginacion.pagina,
        tamano_pagina=paginacion.tamano_pagina,
    )
    total_paginas = math.ceil(total / paginacion.tamano_pagina) if total > 0 else 1

    return {
        'data': [_sesion_a_json(s) for s in sesiones],
        'total': total,
        'pagina': paginacion.pagina,
        'tamano_pagina': paginacion.tamano_pagina,
        'total_paginas': total_paginas,
    }


@router.patch('/{sesion_id}/revocar', status_code=status.HTTP_200_OK)
def revocar_sesion(
    sesion_id: UUID,
    http_request: Request,
    admin: Usuario = Depends(permisos_requeridos('VER_SESIONES')),
    use_case: RevocarSesionAdminUseCase = Depends(get_revocar_sesion_admin_use_case),
):
    use_case.ejecutar(
        sesion_id=sesion_id,
        admin_rut=admin.rut,
        admin_nombre=admin.nombre,
        contexto=construir_contexto_peticion(http_request),
    )
    return {'message': 'Sesión revocada exitosamente'}


@router.patch('/usuario/{rut_usuario}/revocar-todas', status_code=status.HTTP_200_OK)
def revocar_todas_sesiones_usuario(
    rut_usuario: str,
    http_request: Request,
    admin: Usuario = Depends(permisos_requeridos('VER_SESIONES')),
    use_case: RevocarTodasSesionesUsuarioAdminUseCase = Depends(
        get_revocar_todas_sesiones_usuario_admin_use_case
    ),
):
    use_case.ejecutar(
        rut_usuario=rut_usuario,
        admin_rut=admin.rut,
        admin_nombre=admin.nombre,
        contexto=construir_contexto_peticion(http_request),
    )
    return {'message': 'Todas las sesiones del usuario han sido revocadas'}