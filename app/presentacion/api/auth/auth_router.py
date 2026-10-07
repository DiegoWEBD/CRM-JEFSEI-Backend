from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.config import settings
from app.dominio.auth.exceptions import RefreshTokenInvalidoError, RefreshTokenReusadoError
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.auth.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.auth.dependencias.rate_limiter import rate_limit_login
from app.presentacion.api.auth.dependencias.get_cerrar_sesion_use_case import get_cerrar_sesion_use_case
from app.presentacion.api.auth.dependencias.get_cerrar_todas_las_sesiones_use_case import get_cerrar_todas_las_sesiones_use_case
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from app.presentacion.api.auditoria.lib.construir_contexto_peticion import construir_contexto_peticion
from app.presentacion.api.auth.schemas.auth import (
    IniciarSesionRequest,
    TokenResponse,
    RefreshRequest,
    RefreshResponse,
)
from app.aplicacion.auth.use_cases.refrescar_token import RefrescarTokenUseCase
from app.aplicacion.auth.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.aplicacion.auth.use_cases.cerrar_todas_las_sesiones import CerrarTodasLasSesionesUseCase
from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.presentacion.api.auth.dependencias.get_iniciar_sesion_use_case import get_iniciar_sesion_use_case
from app.presentacion.api.auth.dependencias.get_refrescar_token_use_case import get_refrescar_token_use_case

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit_login)],
)
def login(
    payload: IniciarSesionRequest,
    http_request: Request,
    use_case: IniciarSesionUseCase = Depends(get_iniciar_sesion_use_case),
):
    response = use_case.execute(
        rut=payload.rut,
        password=payload.password,
        contexto=construir_contexto_peticion(http_request),
    )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    return TokenResponse(
        access_token=response.access_token,
        refresh_token=response.refresh_token,
        token_type=response.token_type,
        expire_minutes=response.expire_minutes,
        usuario=UsuarioJsonAdapter.Adapt(response.usuario)
    )


@router.post('/refresh', response_model=RefreshResponse, status_code=status.HTTP_200_OK)
def refresh(
    body: RefreshRequest,
    use_case: RefrescarTokenUseCase = Depends(get_refrescar_token_use_case),
):
    """Rota el refresh token y emite un nuevo access token.

    El BFF (Next.js) lee la cookie ``refresh_token`` del navegador, la envía
    aquí en el body, y setea las nuevas cookies en la respuesta al cliente.
    El access token se arma con los claims del usuario actualizado en la
    base de datos (mismos claims que el login).
    """
    try:
        print('[auth] /auth/refresh: recibida petición de rotación', flush=True)
        response = use_case.execute(body.refresh_token)
    except RefreshTokenInvalidoError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )
    except RefreshTokenReusadoError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión comprometida: se detectó reutilización del token",
        )

    return RefreshResponse(
        access_token=response.access_token,
        refresh_token=response.refresh_token,
        token_type=response.token_type,
        expire_minutes=response.expire_minutes,
    )


@router.post('/logout', status_code=status.HTTP_200_OK)
def logout(
    http_request: Request,
    usuario: Usuario = Depends(get_current_user),
    use_case: CerrarSesionUseCase = Depends(get_cerrar_sesion_use_case),
):
    """Revoca la sesión actual y registra el cierre en auditoría."""
    sid = getattr(http_request.state, 'sid', None)
    sesion_id = UUID(sid) if sid else None

    use_case.ejecutar(
        rut=usuario.rut,
        nombre=usuario.nombre,
        sesion_id=sesion_id,
        contexto=construir_contexto_peticion(http_request),
    )

    return {'message': 'Logout exitoso'}


@router.post('/logout-all', status_code=status.HTTP_200_OK)
def logout_all(
    http_request: Request,
    usuario: Usuario = Depends(get_current_user),
    use_case: CerrarTodasLasSesionesUseCase = Depends(get_cerrar_todas_las_sesiones_use_case),
):
    """Revoca todas las sesiones activas del usuario (todos los dispositivos)."""
    use_case.ejecutar(
        rut=usuario.rut,
        nombre=usuario.nombre,
        contexto=construir_contexto_peticion(http_request),
    )

    return {'message': 'Todas las sesiones han sido cerradas'}


@router.post('/ws-ticket', status_code=status.HTTP_200_OK)
def crear_ticket_websocket(
    http_request: Request,
    usuario: Usuario = Depends(permisos_requeridos('VER_ALERTAS')),
):
    """Ticket efímero para abrir el WebSocket de notificaciones.

    Incluye el ``sid`` de la sesión para que el handshake valide que la
    sesión sigue viva.
    """
    sid = getattr(http_request.state, 'sid', None)
    auth_service = JwtAuthenticationService(RepositorioSesionesPostgres())
    ticket = auth_service.crear_ticket_websocket(usuario.rut, sid or '')

    return {
        'ticket': ticket,
        'expira_en': settings.CRM_WS_TICKET_TTL_SEGUNDOS,
    }
