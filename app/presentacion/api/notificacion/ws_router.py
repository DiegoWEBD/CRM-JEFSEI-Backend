"""Endpoint WebSocket que avisa a los clientes cuándo refrescar sus alertas.

No recibe cookies de sesión: el navegador no envía la cookie ``token`` (que fija
Next.js en su propio origen) al conectar directo con el backend. Por eso el
cliente pide antes un ticket efímero a ``POST /auth/ws-ticket`` y lo manda como
query string.

El handshake de un WebSocket **no está cubierto por CORS**: el ``Origin`` se
valida manualmente contra ``settings.origenes_permitidos``.
"""

import asyncio
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.core.config import settings
from app.core.hub_notificaciones import (
    EVENTO_CONEXION_ABIERTA,
    EVENTO_PING,
    hub,
)
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.presentacion.api.usuario.deps import get_obtener_usuario_use_case

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/ws', tags=['WebSocket'])

PERMISO_REQUERIDO = 'VER_ALERTAS'
CODIGO_NO_AUTORIZADO = 1008


def _origen_permitido(websocket: WebSocket) -> bool:
    origen = websocket.headers.get('origin')
    # Los navegadores siempre envían Origin; ausente solo en clientes de prueba
    # (wscat, TestClient), que no plantean el riesgo de un sitio cruzado.
    if not origen:
        return True
    return origen in settings.origenes_permitidos


def _usuario_autorizado(
    use_case: ObtenerUsuarioUseCase,
    rut: str,
) -> Usuario | None:
    """Usuario habilitado con el permiso de alertas; ``None`` si no corresponde."""
    try:
        usuario = use_case.ejecutar(rut)
    except Exception:
        logger.exception('No se pudo cargar el usuario %s para el WebSocket', rut)
        return None

    if not usuario.habilitado or usuario.eliminado:
        return None

    for rol in getattr(usuario, 'roles', []):
        for permiso in getattr(rol, 'permisos', []):
            if getattr(permiso, 'codigo', None) == PERMISO_REQUERIDO:
                return usuario

    return None


def _desempaquetar_ticket(ticket: str | None) -> str | None:
    if not ticket:
        return None
    payload = JwtAuthenticationService().decodificar_token(ticket)
    if not payload or payload.get('proposito') != 'ws':
        return None
    rut = payload.get('rut')
    return rut if isinstance(rut, str) and rut else None


async def _reenviar(websocket: WebSocket, cola: asyncio.Queue) -> None:
    """Pasa los eventos del hub al cliente y mantiene viva la conexión."""
    while True:
        try:
            payload = await asyncio.wait_for(
                cola.get(),
                timeout=settings.CRM_WS_HEARTBEAT_SEGUNDOS,
            )
        except asyncio.TimeoutError:
            await websocket.send_json({'evento': EVENTO_PING})
            continue
        await websocket.send_json(payload)


async def _escuchar(websocket: WebSocket) -> None:
    """Espera mensajes del cliente (o su desconexión)."""
    while True:
        await websocket.receive_text()


@router.websocket('/notificaciones')
async def ws_notificaciones(
    websocket: WebSocket,
    use_case: ObtenerUsuarioUseCase = Depends(get_obtener_usuario_use_case),
) -> None:
    if not _origen_permitido(websocket):
        await websocket.close(code=CODIGO_NO_AUTORIZADO)
        return

    rut = _desempaquetar_ticket(websocket.query_params.get('ticket'))
    if not rut:
        await websocket.close(code=CODIGO_NO_AUTORIZADO)
        return

    usuario = _usuario_autorizado(use_case, rut)
    if usuario is None:
        await websocket.close(code=CODIGO_NO_AUTORIZADO)
        return

    await websocket.accept()
    cola = hub.suscribir(usuario.rut)
    logger.info(
        'WebSocket de notificaciones abierto para %s (%s conexiones)',
        usuario.rut,
        hub.conexiones_de(usuario.rut),
    )

    try:
        await websocket.send_json({'evento': EVENTO_CONEXION_ABIERTA})

        while True:
            tareas = {
                asyncio.create_task(_reenviar(websocket, cola)),
                asyncio.create_task(_escuchar(websocket)),
            }
            hechas, pendientes = await asyncio.wait(
                tareas,
                return_when=asyncio.FIRST_COMPLETED,
            )
            for tarea in pendientes:
                tarea.cancel()
            # Propaga WebSocketDisconnect / RuntimeError de la conexión cerrada.
            for tarea in hechas:
                tarea.result()
    except WebSocketDisconnect:
        logger.info(
            'WebSocket de notificaciones cerrado para %s (%s conexiones)',
            usuario.rut,
            hub.conexiones_de(usuario.rut),
        )
    finally:
        hub.desuscribir(usuario.rut, cola)
