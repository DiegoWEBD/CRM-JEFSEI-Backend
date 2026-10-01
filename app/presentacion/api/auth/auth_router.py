import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.aplicacion.auth.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.aplicacion.auth.use_cases.rotar_sesion import RotarSesionUseCase
from app.dominio.auditoria.repositorio_sesiones import TokenRotadoInvalido
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.usuario.adaptadores.usuario_json_adapter import UsuarioJsonAdapter
from app.presentacion.api.auth.dependencias.get_iniciar_sesion_use_case import get_iniciar_sesion_use_case
from app.presentacion.api.auth.dependencias.get_sesion_use_cases import (
    get_cerrar_sesion_use_case,
    get_rotar_sesion_use_case,
)
from app.presentacion.api.auth.schemas.auth import (
    IniciarSesionRequest,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    TokenResponse,
)
from app.presentacion.api.usuario.dto.usuario_json import UsuarioJson

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/auth', tags=['auth'])
# Alias conservado: main.py y los tests importan el módulo y usan ``router``.
auth_router = router


def _token_response(dto) -> TokenResponse:
    return TokenResponse(
        access_token=dto.access_token,
        token_type=dto.token_type,
        expire_minutes=dto.expire_minutes,
        usuario=UsuarioJsonAdapter.Adapt(dto.usuario),
    )


@router.post('/login', response_model=TokenResponse)
def login(datos: IniciarSesionRequest, response: Response, request: Request,
          use_case: IniciarSesionUseCase = Depends(get_iniciar_sesion_use_case)):
    result = use_case.execute(
        datos.rut,
        datos.password,
        scope=request.scope,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Credenciales inválidas'
        )

    # El access token va en cookie HttpOnly para que el JS de la página no lo
    # pueda leer; el refresh token se devuelve en el cuerpo porque el frontend
    # lo necesita reenviar explícitamente.
    response.set_cookie(
        key='token',
        value=result.access_token,
        httponly=True,
        samesite='lax',
        secure=True,
        path='/',
    )

    return _token_response(result)


@router.post('/refresh', response_model=RefreshResponse)
def refresh(datos: RefreshRequest, response: Response, request: Request,
            use_case: RotarSesionUseCase = Depends(get_rotar_sesion_use_case)):
    refresh_token = datos.refresh_token or request.cookies.get('refresh_token', '')

    try:
        result = use_case.execute(refresh_token, scope=request.scope)
    except TokenRotadoInvalido as error:
        # El motivo nunca sale hacia el cliente: distinguir "expirado" de
        # "reutilizado" le diría a quien tenga el token cómo va el estado de la
        # sesión. Va al log técnico, la respuesta es genérica.
        logger.info('REFRESH_REJECTED motivo=%s', error.motivo)
        response.delete_cookie('token', path='/')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Usuario no autenticado'
        )

    response.set_cookie(
        key='token',
        value=result.access_token,
        httponly=True,
        samesite='lax',
        secure=True,
        path='/',
    )

    # En una rotación duplicada dentro de la ventana de gracia el refresh_token
    # viene vacío: el cliente ya tiene el par de la llamada original, así que
    # no se le manda un token en blanco que pise el bueno.
    return RefreshResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        expire_minutes=result.expire_minutes,
        id_sesion=result.id_sesion,
        refresh_token=result.refresh_token,
    )


@router.post('/logout', response_model=LogoutResponse)
def logout(response: Response, request: Request,
           use_case: CerrarSesionUseCase = Depends(get_cerrar_sesion_use_case)):
    # El id de sesión se saca del access token: es la única prueba de que quien
    # llama era el dueño de esa sesión, sin exponerlo en un cuerpo o query.
    id_sesion = None
    token = request.cookies.get('token')
    if token:
        payload = JwtAuthenticationService().decodificar_token(token)
        if payload:
            id_sesion = payload.get('jti')

    use_case.execute(id_sesion, scope=request.scope)

    response.delete_cookie('token', path='/')
    response.delete_cookie('refresh_token', path='/')
    response.delete_cookie('device_id', path='/')

    return LogoutResponse()
