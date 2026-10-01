from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.config import settings
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.auth.dependencias.get_cerrar_sesion_use_case import get_cerrar_sesion_use_case
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from app.presentacion.api.auditoria.lib.construir_contexto_peticion import construir_contexto_peticion
from app.presentacion.api.auth.schemas.auth import IniciarSesionRequest, TokenResponse
from app.aplicacion.auth.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.presentacion.api.auth.dependencias.get_iniciar_sesion_use_case import get_iniciar_sesion_use_case

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    payload: IniciarSesionRequest,
    http_request: Request,
    use_case: IniciarSesionUseCase = Depends(get_iniciar_sesion_use_case)
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
        token_type=response.token_type,
        expire_minutes=response.expire_minutes,
        usuario=UsuarioJsonAdapter.Adapt(response.usuario)
    )


@router.post('/logout', status_code=status.HTTP_200_OK)
def logout(
    http_request: Request,
    usuario: Usuario = Depends(get_current_user),
    use_case: CerrarSesionUseCase = Depends(get_cerrar_sesion_use_case),
):
    """Registra el cierre de sesión en la bitácora de auditoría.

    La cookie de sesión la borra el BFF (Next.js); este endpoint deja constancia
    del cierre mientras el token sigue vigente.
    """
    use_case.ejecutar(
        rut=usuario.rut,
        nombre=usuario.nombre,
        contexto=construir_contexto_peticion(http_request),
    )

    return {'message': 'Logout exitoso'}


@router.post('/ws-ticket', status_code=status.HTTP_200_OK)
def crear_ticket_websocket(
    usuario: Usuario = Depends(permisos_requeridos('VER_ALERTAS')),
):
    """Ticket efímero para abrir el WebSocket de notificaciones.

    El navegador no puede leer la cookie httpOnly ``token`` (la fija Next.js en
    su origen) y el handshake directo con el backend no la incluye, así que el
    cliente intercambia aquí la cookie por un ticket de un solo propósito.
    """
    ticket = JwtAuthenticationService().crear_ticket_websocket(usuario.rut)

    return {
        'ticket': ticket,
        'expira_en': settings.CRM_WS_TICKET_TTL_SEGUNDOS,
    }