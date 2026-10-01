# app/core/contextos.py
"""Estado de correlación que sobrevive a la request.

El ``request_id`` vive en un ContextVar para que el filtro de logging pueda
enriquecer cada línea sin que haya que pasarlo por parámetro. No se usa para
decidir quién es el usuario: eso sale de la sesión validada por el backend.
"""

import uuid
from contextvars import ContextVar

_request_id: ContextVar[str | None] = ContextVar('request_id', default=None)


def establecer_request_id(request_id: str) -> str:
    """Fija el id de correlación del hilo/task actual y lo devuelve."""
    _request_id.set(request_id)
    return request_id


def obtener_request_id() -> str | None:
    return _request_id.get()


def limpiar_request_id() -> None:
    _request_id.set(None)


def nuevo_request_id() -> str:
    return str(uuid.uuid4())
