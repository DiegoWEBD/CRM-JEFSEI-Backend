from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.aplicacion.rol.use_cases.asignar_permisos_rol import AsignarPermisosRolUseCase
from app.aplicacion.rol.use_cases.obtener_roles import ObtenerRolesUseCase
from app.aplicacion.rol.use_cases.obtener_roles_con_permisos import ObtenerRolesConPermisosUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auditoria.lib.construir_contexto_peticion import construir_contexto_peticion
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.rol.deps import (
    get_asignar_permisos_rol_use_case,
    get_obtener_roles_con_permisos_use_case,
    get_obtener_roles_use_case,
)
from app.presentacion.api.rol.dto.asignar_permisos_rol_request import AsignarPermisosRolRequest


router = APIRouter(prefix='/roles', tags=['Roles'])


@router.get('/', status_code=status.HTTP_200_OK)
def obtener_roles(
    usuario: Usuario = Depends(permisos_requeridos('OBTENER_ROLES')),
    use_case: ObtenerRolesUseCase = Depends(get_obtener_roles_use_case)
):
    roles = use_case.ejecutar()

    return {
        'roles': [
            {
                'codigo': rol.codigo,
                'nombre': rol.nombre
            }
            for rol in roles
        ]
    }


@router.get('/con-permisos', status_code=status.HTTP_200_OK)
def obtener_roles_con_permisos(
    _ = Depends(permisos_requeridos('ADMINISTRAR_ROLES')),
    use_case: ObtenerRolesConPermisosUseCase = Depends(get_obtener_roles_con_permisos_use_case)
):
    roles = use_case.ejecutar()

    return {
        'data': roles
    }


@router.put('/{codigo}/permisos', status_code=status.HTTP_200_OK)
def asignar_permisos_rol(
    codigo: str,
    request: AsignarPermisosRolRequest,
    http_request: Request,
    usuario: Usuario = Depends(permisos_requeridos('ADMINISTRAR_ROLES')),
    use_case: AsignarPermisosRolUseCase = Depends(get_asignar_permisos_rol_use_case)
):
    actualizado = use_case.ejecutar(
        codigo_rol=codigo,
        codigos_permiso=request.codigos_permiso,
        usuario_ejecutor=usuario,
        contexto=construir_contexto_peticion(http_request),
    )

    if not actualizado:
        raise HTTPException(
            status_code=400,
            detail='Error al asignar los permisos al rol'
        )

    return {
        'message': 'Permisos del rol actualizados correctamente'
    }
