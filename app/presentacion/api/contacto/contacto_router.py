from fastapi import APIRouter, Depends, status

from app.aplicacion.contacto.use_cases.actualizar_contacto import ActualizarContactoUseCase
from app.aplicacion.contacto.use_cases.eliminar_contacto import EliminarContactoUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.contacto.adaptadores.contacto_json_adapter import ContactoJsonAdapter
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.contacto.dependencias.deps import (
    get_actualizar_contacto_use_case,
    get_eliminar_contacto_use_case,
)
from app.presentacion.api.contacto.dto.actualizar_contacto_request import ActualizarContactoRequest


router = APIRouter(prefix='/contactos', tags=['Contactos'])


@router.put('/{id}', status_code=status.HTTP_200_OK)
def actualizar_contacto(
    id: int,
    request: ActualizarContactoRequest,
    usuario: Usuario = Depends(permisos_requeridos('ACTUALIZAR_CONTACTO_TODOS', 'ACTUALIZAR_CONTACTO_PROPIOS')),
    use_case: ActualizarContactoUseCase = Depends(get_actualizar_contacto_use_case),
):
    contacto = use_case.ejecutar(
        id=id,
        nombre=request.nombre,
        telefono=request.telefono,
        correo=request.correo,
        cargo=request.cargo,
        rut_usuario=usuario.rut,
    )

    return {
        'data': ContactoJsonAdapter(contacto).to_json(),
        'message': 'Contacto actualizado correctamente'
    }


@router.delete('/{id}', status_code=status.HTTP_200_OK)
def eliminar_contacto(
    id: int,
    usuario: Usuario = Depends(permisos_requeridos('ELIMINAR_CONTACTO_TODOS', 'ELIMINAR_CONTACTO_PROPIOS')),
    use_case: EliminarContactoUseCase = Depends(get_eliminar_contacto_use_case),
):
    use_case.ejecutar(id=id, rut_usuario=usuario.rut)

    return {
        'message': 'Contacto eliminado correctamente'
    }