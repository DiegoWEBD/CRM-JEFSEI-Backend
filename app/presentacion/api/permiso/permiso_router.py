from fastapi import APIRouter, Depends, status

from app.aplicacion.permiso.use_cases.obtener_permisos import ObtenerPermisosUseCase
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.permiso.deps import get_obtener_permisos_use_case


router = APIRouter(prefix='/permisos', tags=['Permisos'])


@router.get('/', status_code=status.HTTP_200_OK)
def obtener_permisos(
    _ = Depends(permisos_requeridos('ADMINISTRAR_ROLES')),
    use_case: ObtenerPermisosUseCase = Depends(get_obtener_permisos_use_case)
):
    permisos = use_case.ejecutar()

    return {
        'data': [
            {
                'codigo': permiso.codigo,
                'descripcion': permiso.descripcion
            }
            for permiso in permisos
        ]
    }
