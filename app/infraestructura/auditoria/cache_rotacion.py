"""Caché de rotación single-flight, en memoria y efímera.

Por qué existe: el BFF dispara peticiones en paralelo (prefetch SSR más
react-query), así que dos refresh con el mismo token pueden llegar juntos. Sin
esto, el segundo parecería un robo de token y tiraría la sesión del usuario
legítimamente.

Por qué en memoria y no en la base: el refresh token se guarda **solo como
hash**, por lo que el servidor no puede volver a emitir el token vigente cuando
detecta un duplicado. Guardar el par recién emitido durante la ventana de gracia
resuelve el caso sin guardar nada sensible de forma persistente, y al expirar
la ventana la entrada desaparece sola.

En un despliegue con varias instancias esta caché no se comparte, así que una
rotación duplicada que caiga en otra instancia se trata como robo. Es la
dirección segura del fallo y, con una sola instancia, no ocurre.
"""

import threading
import time
from typing import Optional

from app.core.config import settings


class CacheRotacion:
    def __init__(self) -> None:
        self._datos: dict[str, tuple[float, object]] = {}
        self._lock = threading.Lock()

    def guardar(self, hash_anterior: str, valor: object) -> None:
        ventana = settings.REFRESH_TOKEN_REUSE_GRACE_SEGUNDOS
        if ventana <= 0:
            return
        with self._lock:
            self._purgar()
            self._datos[hash_anterior] = (time.monotonic() + ventana, valor)

    def obtener(self, hash_anterior: str) -> Optional[object]:
        with self._lock:
            self._purgar()
            entrada = self._datos.get(hash_anterior)
            if entrada is None:
                return None
            vence, valor = entrada
            if vence < time.monotonic():
                del self._datos[hash_anterior]
                return None
            return valor

    def _purgar(self) -> None:
        ahora = time.monotonic()
        vencidas = [k for k, (vence, _) in self._datos.items() if vence < ahora]
        for clave in vencidas:
            del self._datos[clave]

    def limpiar(self) -> None:
        with self._lock:
            self._datos.clear()


cache_rotacion = CacheRotacion()
