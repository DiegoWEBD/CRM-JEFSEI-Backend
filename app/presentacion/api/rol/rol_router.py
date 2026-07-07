from fastapi import APIRouter, Depends, status

from app.aplicacion.rol.use_cases.obtener_roles import ObtenerRolesUseCase
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.rol.deps import get_obtener_roles_use_case


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
