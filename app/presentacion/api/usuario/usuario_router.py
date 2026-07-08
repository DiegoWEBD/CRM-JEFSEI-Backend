from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.aplicacion.recordatorio.use_cases.obtener_proximo_contacto import ObtenerProximoContactoUseCase
from app.aplicacion.usuario.use_cases.actualizar_usuario import ActualizarUsuarioUseCase
from app.aplicacion.usuario.use_cases.eliminar_usuario import EliminarUsuarioUseCase
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.aplicacion.usuario.use_cases.obtener_usuarios import ObtenerUsuariosUseCase
from app.aplicacion.usuario.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.recordatorio.dependencias.deps import get_obtener_proximo_contacto_use_case
from app.presentacion.api.usuario.deps import get_actualizar_usuario_use_case, get_eliminar_usuario_use_case, get_obtener_usuario_use_case, get_obtener_usuarios_use_case, get_registrar_usuario_use_case
from app.presentacion.api.usuario.dto.actualizar_usuario_request import ActualizarUsuarioRequest
from app.presentacion.api.usuario.dto.registrar_usuario_request import RegistrarUsuarioRequest

router = APIRouter(prefix='/usuarios', tags=['Usuarios'])

@router.get('/', status_code=status.HTTP_200_OK)
def obtener_usuarios(
    _ = Depends(permisos_requeridos('OBTENER_USUARIOS')),
    use_case: ObtenerUsuariosUseCase = Depends(get_obtener_usuarios_use_case)
):
    usuarios = use_case.ejecutar()

    return {
        'data': [UsuarioJsonAdapter.Adapt(usuario) for usuario in usuarios]
    }

@router.get('/{rut}', status_code = status.HTTP_200_OK)
def obtener_usuario(
    rut: str,
    use_case: ObtenerUsuarioUseCase = Depends(get_obtener_usuario_use_case)
):
    usuario = use_case.ejecutar(rut)

    return {
        'data': UsuarioJsonAdapter.Adapt(usuario)
    }


@router.get('/{rut}/recordatorios/proximo-contacto', status_code=status.HTTP_200_OK)
def obtener_proximo_contacto(
    rut: str,
    id_prospecto: int = Query(),
    use_case: ObtenerProximoContactoUseCase = Depends(get_obtener_proximo_contacto_use_case),
):
    recordatorio = use_case.ejecutar(rut_usuario=rut, id_prospecto=id_prospecto)
    return {'data': recordatorio}
    

@router.post('/', status_code = status.HTTP_201_CREATED)
def registrar_usuario(
    request: RegistrarUsuarioRequest,
    _ = Depends(permisos_requeridos('REGISTRAR_USUARIOS')),
    use_case: RegistrarUsuarioUseCase = Depends(get_registrar_usuario_use_case)
):
    registrado = use_case.ejecutar(
        rut=request.rut,
        nombre=request.nombre,
        correo=request.correo,
        telefono=request.telefono,
        id_sucursal=request.id_sucursal,
        password=request.password,
        codigo_roles=request.codigo_roles,
        meta_mensual_uf=request.meta_mensual_uf,
        porcentaje_comision=request.porcentaje_comision,
    )

    if not registrado:
        raise HTTPException(
            status_code=400,
            detail='Error al registrar el usuario'
        )

    return {
        'message': 'Usuario registrado correctamente'
    }


@router.put('/{rut}', status_code=status.HTTP_200_OK)
def actualizar_usuario(
    rut: str,
    request: ActualizarUsuarioRequest,
    _ = Depends(permisos_requeridos('ADMINISTRAR_USUARIOS')),
    use_case: ActualizarUsuarioUseCase = Depends(get_actualizar_usuario_use_case)
):
    actualizado = use_case.ejecutar(
        rut=rut,
        nombre=request.nombre,
        correo=request.correo,
        telefono=request.telefono,
        id_sucursal=request.id_sucursal,
        password=request.password,
        codigo_roles=request.codigo_roles,
        meta_mensual_uf=request.meta_mensual_uf,
        porcentaje_comision=request.porcentaje_comision,
        habilitado=request.habilitado
    )

    if not actualizado:
        raise HTTPException(
            status_code=400,
            detail='Error al actualizar el usuario'
        )

    return {
        'message': 'Usuario actualizado correctamente'
    }


@router.delete('/{rut}', status_code=status.HTTP_200_OK)
def eliminar_usuario(
    rut: str,
    _ = Depends(permisos_requeridos('ADMINISTRAR_USUARIOS')),
    use_case: EliminarUsuarioUseCase = Depends(get_eliminar_usuario_use_case)
):
    use_case.ejecutar(rut)

    return {
        'message': 'Usuario eliminado correctamente'
    }