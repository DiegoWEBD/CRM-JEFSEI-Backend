"""Hub en memoria de conexiones WebSocket de notificaciones, agrupadas por RUT.

El backend corre con un único proceso (ver ``backend/Dockerfile``:
``uvicorn app.main:app`` sin ``--workers``), por lo que este singleton es
suficiente. Si se escala a varios workers o réplicas, las publicaciones deben
pasar por un broker externo (p. ej. Redis pub/sub).

Los puntos de publicación (scheduler de alertas y endpoints de marcar leída)
corren en *threads*, fuera del event loop: por eso la API pública es
``publicar_desde_hilo``, que programa la publicación en el loop principal.
"""

import asyncio
import logging
from collections.abc import Iterable
from typing import Any

logger = logging.getLogger(__name__)

EVENTO_NOTIFICACIONES_ACTUALIZADAS = 'notificaciones_actualizadas'
EVENTO_CONEXION_ABIERTA = 'conexion_abierta'
EVENTO_PING = 'ping'


class HubNotificaciones:
    def __init__(self) -> None:
        self._suscripciones: dict[str, set[asyncio.Queue[dict[str, Any]]]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def capturar_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Guarda el event loop principal (se llama desde el lifespan de FastAPI)."""
        self._loop = loop

    @property
    def loop(self) -> asyncio.AbstractEventLoop | None:
        return self._loop

    def suscribir(self, rut: str) -> asyncio.Queue[dict[str, Any]]:
        """Registra una conexión y devuelve su cola de eventos."""
        cola: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=32)
        self._suscripciones.setdefault(rut, set()).add(cola)
        return cola

    def desuscribir(self, rut: str, cola: asyncio.Queue[dict[str, Any]]) -> None:
        """Baja la conexión. Síncrono a propósito: se ejecuta en un ``finally``
        que también corre durante una cancelación, donde un ``await`` adicional
        podría no llegar a ejecutarse."""
        suscripciones = self._suscripciones.get(rut)
        if not suscripciones:
            return
        suscripciones.discard(cola)
        if not suscripciones:
            self._suscripciones.pop(rut, None)

    def conexiones_de(self, rut: str) -> int:
        return len(self._suscripciones.get(rut, ()))

    @property
    def total_conexiones(self) -> int:
        return sum(len(suscripciones) for suscripciones in self._suscripciones.values())

    def publicar_desde_hilo(
        self,
        ruts: Iterable[str],
        payload: dict[str, Any],
    ) -> None:
        """Publica a los RUT indicados; seguro de llamar desde cualquier thread.

        Nunca lanza: forma parte del camino de cada request que cambia el estado
        de las notificaciones, así que un loop que se está cerrando solo cuesta
        el aviso (el cliente lo recupera al reconectar).
        """
        destinatarios = {rut for rut in ruts if rut}
        if not destinatarios:
            return

        loop = self._loop
        if loop is None or loop.is_closed():
            logger.debug('Sin event loop capturado: se omite la publicación de %s', payload.get('evento'))
            return

        try:
            loop_actual = asyncio.get_running_loop()
        except RuntimeError:
            loop_actual = None

        if loop_actual is loop:
            asyncio.ensure_future(self._publicar(destinatarios, payload))
            return

        try:
            asyncio.run_coroutine_threadsafe(self._publicar(destinatarios, payload), loop)
        except RuntimeError:
            logger.debug('Event loop no disponible: se omite la publicación de %s', payload.get('evento'))

    async def _publicar(self, ruts: set[str], payload: dict[str, Any]) -> None:
        for rut in ruts:
            for cola in tuple(self._suscripciones.get(rut, ())):
                try:
                    cola.put_nowait(payload)
                except asyncio.QueueFull:
                    # La cola llena significa que la conexión no drena eventos:
                    # se descarta el aviso y el cliente se enterará al reconectar.
                    logger.warning('Cola saturada para %s: se descarta %s', rut, payload.get('evento'))


hub = HubNotificaciones()
