from fastapi import Depends, HTTPException, status, Request

from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.presentacion.api.usuario.deps import get_obtener_usuario_use_case


def get_authentication_service() -> AuthenticationService:
    return JwtAuthenticationService()


def get_current_user(
    request: Request,
    authentication_service: AuthenticationService = Depends(get_authentication_service),
    use_case: ObtenerUsuarioUseCase = Depends(get_obtener_usuario_use_case)
) -> Usuario:

    token = request.cookies.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )

    payload = authentication_service.decodificar_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )

    rut: str | None = payload.get("rut")

    if rut is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )

    try:
        usuario = use_case.ejecutar(rut)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )

    if not usuario.habilitado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario deshabilitado"
        )

    if usuario.eliminado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario eliminado"
        )

    return usuario