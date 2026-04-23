from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.presentacion.api.usuario.deps import get_obtener_usuario_use_case

security = HTTPBearer()

def get_authentication_service() -> AuthenticationService:
    return JwtAuthenticationService()

def get_current_user(
    credenciales: HTTPAuthorizationCredentials = Depends(security),
    authentication_service: AuthenticationService = Depends(get_authentication_service),
    use_case: ObtenerUsuarioUseCase = Depends(get_obtener_usuario_use_case)
) -> Usuario:
    token = credenciales.credentials
    print(token)
    payload = authentication_service.decodificar_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    rut: str | None = payload.get("sub")

    if rut is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autorizado"
        )

    try:
        usuario = use_case.ejecutar(rut)

    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autorizado"
        )

    return usuario