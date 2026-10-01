import uuid

from fastapi import Request

from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.infraestructura.auditoria.resolucion_ip import resolver_ip_origen


def construir_contexto_peticion(request: Request) -> ContextoPeticion:
    client_host = request.client.host if request.client else None
    id_peticion = (
        getattr(request.state, 'id_peticion', None)
        or request.headers.get('x-request-id')
        or uuid.uuid4().hex
    )
    return ContextoPeticion(
        ip_origen=resolver_ip_origen(request.headers, client_host),
        user_agent=request.headers.get('user-agent'),
        id_peticion=id_peticion,
    )
