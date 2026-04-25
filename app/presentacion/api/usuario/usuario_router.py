from fastapi import APIRouter, Depends, Response
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.aplicacion.usuario.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.usuario.deps import get_obtener_usuario_use_case, get_registrar_usuario_use_case
from app.presentacion.api.usuario.schemas.registrar_usuario_request import RegistrarUsuarioRequest

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/{rut}")
def obtener_usuario(
    rut: str,
    response: Response,
    use_case: ObtenerUsuarioUseCase = Depends(get_obtener_usuario_use_case)
):
    try:
        usuario = use_case.ejecutar(rut)
        response.status_code = 200

        return {
            'message': 'Usuario obtenido correctamente',
            'data': UsuarioJsonAdapter.Adapt(usuario)
        }

    except Exception as exc:
        response.status_code = 404
        return {
            'message': str(exc)
        }
    

@router.post("/")
def registrar_usuario(
    request: RegistrarUsuarioRequest,
    response: Response,
    _ = Depends(permisos_requeridos('REGISTRAR_USUARIOS')),
    use_case: RegistrarUsuarioUseCase = Depends(get_registrar_usuario_use_case)
):
    try:
        registrado = use_case.ejecutar(
            rut=request.rut,
            nombre=request.nombre,
            correo=request.correo,
            telefono=request.telefono,
            id_sucursal=request.id_sucursal,
            password=request.password,
            codigo_roles=request.codigo_roles
        )

        if registrado:
            response.status_code = 201
            return {
                'message': 'Usuario registrado correctamente'
            }
        else:
            response.status_code = 400
            return {
                'message': 'Error al registrar el usuario'
            }
    except Exception as exc:
        response.status_code = 400
        return {
            'message': str(exc)
        }