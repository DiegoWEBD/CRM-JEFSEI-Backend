from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.presentacion.api.auth.dependencias.permisos_requeridos import permisos_requeridos
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from app.presentacion.api.auth.schemas.auth import IniciarSesionRequest, TokenResponse
from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.presentacion.api.auth.dependencias.get_iniciar_sesion_use_case import get_iniciar_sesion_use_case

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    request: IniciarSesionRequest,
    use_case: IniciarSesionUseCase = Depends(get_iniciar_sesion_use_case)
):
    response = use_case.execute(
        rut=request.rut,
        password=request.password
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