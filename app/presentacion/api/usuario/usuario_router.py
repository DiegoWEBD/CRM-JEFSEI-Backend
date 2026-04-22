from fastapi import APIRouter, Depends
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.presentacion.api.usuario.deps import get_obtener_usuario_use_case

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/{rut}")
def obtener_usuario(
    rut: str,
    use_case: ObtenerUsuarioUseCase = Depends(get_obtener_usuario_use_case)
):
    usuario = use_case.ejecutar(rut)

    return usuario