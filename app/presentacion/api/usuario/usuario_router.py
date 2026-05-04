from fastapi import APIRouter, Depends, HTTPException, status
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.aplicacion.usuario.use_cases.obtener_usuarios import ObtenerUsuariosUseCase
from app.aplicacion.usuario.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.usuario.deps import get_obtener_usuario_use_case, get_obtener_usuarios_use_case, get_registrar_usuario_use_case
from app.presentacion.api.usuario.schemas.registrar_usuario_request import RegistrarUsuarioRequest

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/", status_code=status.HTTP_200_OK)
def obtener_usuarios(
    _ = Depends(permisos_requeridos('OBTENER_USUARIOS')),
    use_case: ObtenerUsuariosUseCase = Depends(get_obtener_usuarios_use_case)
):
    try:
        usuarios = use_case.ejecutar()

        return {
            "data": [UsuarioJsonAdapter.Adapt(usuario) for usuario in usuarios]
        }

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

@router.get("/{rut}", status_code = status.HTTP_200_OK)
def obtener_usuario(
    rut: str,
    use_case: ObtenerUsuarioUseCase = Depends(get_obtener_usuario_use_case)
):
    try:
        usuario = use_case.ejecutar(rut)

        return {
            'data': UsuarioJsonAdapter.Adapt(usuario)
        }

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )
    

@router.post("/", status_code = status.HTTP_201_CREATED)
def registrar_usuario(
    request: RegistrarUsuarioRequest,
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
            codigo_roles=request.codigo_roles,
            meta_mensual_uf=request.meta_mensual_uf
        )

        if not registrado:
            raise HTTPException(
                status_code=400,
                detail="Error al registrar el usuario"
            )

        return {
            "message": "Usuario registrado correctamente"
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )