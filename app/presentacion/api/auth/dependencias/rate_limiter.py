"""Rate limiter en memoria para endpoints sensibles (login).

No requiere dependencias externas. Los contadores se limpian automáticamente
cuando expira su ventana temporal.

Uso:
    from app.presentacion.api.auth.dependencias.rate_limiter import rate_limit_login

    @router.post('/login', dependencies=[Depends(rate_limit_login)])
    def login(...): ...
"""

import json
import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status


class _ContadorRateLimit:
    """Ventana deslizante simple por clave."""

    def __init__(self, max_intentos: int, ventana_segundos: int):
        self.max_intentos = max_intentos
        self.ventana_segundos = ventana_segundos
        self._intentos: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def verificar(self, clave: str) -> None:
        ahora = time.monotonic()
        limite = ahora - self.ventana_segundos

        with self._lock:
            intentos = self._intentos[clave]
            # Limpiar intentos fuera de la ventana
            self._intentos[clave] = [t for t in intentos if t > limite]
            intentos = self._intentos[clave]

            if len(intentos) >= self.max_intentos:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Demasiados intentos. Intente nuevamente en un minuto.",
                )

            intentos.append(ahora)


# 5 intentos por RUT por minuto
_limit_rut = _ContadorRateLimit(max_intentos=5, ventana_segundos=60)
# 20 intentos por IP por minuto
_limit_ip = _ContadorRateLimit(max_intentos=20, ventana_segundos=60)


async def rate_limit_login(request: Request) -> None:
    """Dependencia de FastAPI que limita intentos de login por RUT e IP."""
    rut = ''
    try:
        body = await request.body()
        if body:
            datos = json.loads(body)
            rut = datos.get('rut', '')
    except Exception:
        pass

    ip = request.client.host if request.client else 'unknown'

    if rut:
        _limit_rut.verificar(f"rut:{rut}")
    _limit_ip.verificar(f"ip:{ip}")
