from uuid import UUID

from fastapi import Depends, HTTPException, status, Request

from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.auth.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.presentacion.api.usuario.deps import get_obtener_usuario_use_case


def get_authentication_service() -> AuthenticationService:
    return JwtAuthenticationService(RepositorioSesionesPostgres())


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
    sid_raw: str | None = payload.get("sid")

    if rut is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )

    # Validar que la sesión siga viva (no revocada, no expirada)
    if sid_raw is not None:
        try:
            sesion_id = UUID(sid_raw)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión inválida"
            )

        sesion = authentication_service.obtener_sesion_viva(sesion_id)
        if sesion is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión revocada o expirada"
            )

        # Expone el sid para que endpoints como ws-ticket lo usen
        request.state.sid = sid_raw

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

    # Expone la identidad en request.state para que el middleware de auditoría
    # pueda atribuir la petición sin volver a consultar la base de datos.
    request.state.usuario = usuario

    return usuario
