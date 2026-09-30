"""Middleware ASGI de auditoría y correlación (§13).

Es ASGI puro y no ``BaseHTTPMiddleware`` a propósito. Los endpoints de este
proyecto son ``def`` síncronos, así que Starlette los corre en un threadpool; con
``BaseHTTPMiddleware`` lo que el endpoint escriba en ``contextvars`` no regresa
al middleware. ``scope['state']`` en cambio es el mismo dict durante todo el
ciclo, y es lo que ``get_current_user`` usa para publicar el usuario
autenticado, de modo que el middleware lo ve al terminar.

Responsabilidades: request id, IP, User-Agent, endpoint, duración, status y
cabecera de correlación en la respuesta. No registra eventos de negocio ni
inventa reglas: eso es del AuditService (§13, "no convertir el middleware en un
repositorio de lógica de negocio").
"""

import logging
import re
import time
import uuid
from typing import Optional

from app.core.config import settings
from app.core.contextos import establecer_request_id, limpiar_request_id
from app.infraestructura.auditoria.contexto_auditoria import AuditContext
from app.infraestructura.auditoria.ip import resolver_ip

logger = logging.getLogger(__name__)

# Un X-Request-ID externo solo se acepta si parece un UUID: evita que se cuele
# contenido arbitrario en la base (saltos de línea, payloads grandes) y mantiene
# la correlación NGINX -> Next.js -> FastAPI -> PostgreSQL.
UUID_RE = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
)

# Headers copiados a metadata. Lista explícita: no se guardan todos porque ahí
# viaja la cookie de sesión y el Authorization (§10, §16).
HEADERS_METADATA = (
    'accept-language',
    'accept-encoding',
    'sec-ch-ua',
    'sec-ch-ua-mobile',
    'sec-ch-ua-platform',
)

CLAVE_ESTADO = 'auditoria'


def normalizar_request_id(crudo: Optional[str]) -> str:
    """Reutiliza el X-Request-ID entrante si es un UUID válido; si no, genera uno."""
    if crudo:
        candidato = crudo.strip()
        if UUID_RE.match(candidato):
            return candidato
    return str(uuid.uuid4())


def _device_id_desde_cookies(cabecera_cookie: str) -> Optional[str]:
    """device_id es un UUID generado por el cliente, nunca un fingerprint (§11).

    Viaja como cookie httpOnly que el BFF reenvía dentro del header Cookie.
    """
    for parte in cabecera_cookie.split(';'):
        nombre, _, valor = parte.strip().partition('=')
        if nombre == 'device_id' and UUID_RE.match(valor):
            return valor
    return None


class MiddlewareAuditoria:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        headers = {
            k.decode('latin-1'): v.decode('latin-1')
            for k, v in (scope.get('headers') or [])
        }

        request_id = normalizar_request_id(headers.get(settings.AUDIT_REQUEST_ID_HEADER.lower()))
        establecer_request_id(request_id)

        peer = scope['client'][0] if scope.get('client') else None
        path = scope.get('path', '')
        metodo = scope.get('method', '')

        metadata: dict = {}
        for nombre in HEADERS_METADATA:
            if headers.get(nombre):
                metadata[nombre] = headers[nombre]

        contexto = AuditContext(
            request_id=request_id,
            ip_origen=resolver_ip(
                peer,
                headers.get('x-forwarded-for'),
                headers.get('x-real-ip'),
            ),
            user_agent=headers.get('user-agent') if settings.AUDIT_STORE_USER_AGENT else None,
            device_id=_device_id_desde_cookies(headers.get('cookie', ''))
            if settings.AUDIT_STORE_DEVICE_METADATA else None,
            metodo_http=metodo,
            endpoint=path,
            path=path,
            origin=headers.get('origin'),
            referer=headers.get('referer'),
            metadata=metadata,
        )

        # El mismo dict que ven los endpoints vía request.state. Acá se publica
        # el contexto base; get_current_user lo enriquece con el usuario.
        scope.setdefault('state', {})[CLAVE_ESTADO] = contexto

        inicio = time.perf_counter()
        status_por_defecto = {'valor': 500}

        async def send_wrapper(mensaje):
            if mensaje['type'] == 'http.response.start':
                status_por_defecto['valor'] = mensaje['status']
                cabeceras = list(mensaje.get('headers') or [])
                cabeceras.append((
                    settings.AUDIT_REQUEST_ID_HEADER.encode('latin-1'),
                    request_id.encode('latin-1'),
                ))
                mensaje = {**mensaje, 'headers': cabeceras}
            await send(mensaje)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            logger.exception(
                'Error no controlado en %s %s', metodo, path,
                extra={'request_id': request_id, 'metodo_http': metodo, 'path': path},
            )
            raise
        finally:
            # Se deja el contexto final con status y duración disponibles para
            # cualquier registro de auditoría que ocurra después del handler.
            contexto.status_http = status_por_defecto['valor']
            contexto.duracion_ms = int((time.perf_counter() - inicio) * 1000)
            limpiar_request_id()
