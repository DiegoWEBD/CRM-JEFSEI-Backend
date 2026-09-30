"""Resolución segura de la IP real del cliente.

La API queda detrás de NGINX en el VPS, pero en local corre expuesta
directamente. La diferencia la decide ``AUDIT_TRUSTED_PROXIES``:

- lista vacía (local): se usa el peer de la conexión y ``X-Forwarded-For`` se
  descarta por completo, porque cualquiera podría enviarla para falsear la IP.
- lista con la IP/CIDR del NGINX: se toma la IP real del header, y sólo de la
  parte de la cadena que está a la izquierda de un proxy conocido.

Confiar en XFF sin validar el par de conexiones es el error clásico: cualquier
cliente puede mandar ``X-Forwarded-For: 1.2.3.4`` y aparecer con esa IP.

``resolver_ip`` es la función pura (peer, headers) -> IP. La usan tanto
``get_client_ip`` como el middleware ASGI, para que la regla exista en un solo
sitio (§41).
"""

from ipaddress import ip_address, ip_network
from typing import Optional

from fastapi import Request

from app.core.config import settings

_cache_redes: Optional[list] = None


def _redes_confiables() -> list:
    global _cache_redes
    if _cache_redes is None:
        redes = []
        for entrada in settings.proxies_auditoria_confiables:
            try:
                redes.append(ip_network(entrada, strict=False))
            except ValueError:
                # Una entrada mal formada no debe tumbar la auditoría: se ignora
                # y se sigue con el peer de la conexión.
                continue
        _cache_redes = redes
    return _cache_redes


def es_proxy_confiable(ip: str | None) -> bool:
    if not ip:
        return False
    try:
        direccion = ip_address(ip)
    except ValueError:
        return False
    return any(direccion in red for red in _redes_confiables())


def normalizar(ip: str | None) -> Optional[str]:
    if not ip:
        return None
    try:
        return str(ip_address(ip.strip()))
    except ValueError:
        return None


def resolver_ip(
    peer: str | None,
    x_forwarded_for: str | None = None,
    x_real_ip: str | None = None,
) -> Optional[str]:
    """Regla única de resolución. No lanza nunca."""
    if not es_proxy_confiable(peer):
        # Acceso directo: el peer ES el cliente. Los headers se ignoran.
        return normalizar(peer)

    if x_forwarded_for:
        candidatos = [p.strip() for p in x_forwarded_for.split(',') if p.strip()]

        # El barrido va de DERECHA a IZQUIERDA a propósito. NGINX usa
        # $proxy_add_x_forwarded_for, que ANTEPONE lo que el cliente ya había
        # mandado: si el cliente envía "X-Forwarded-For: 1.1.1.1", NGINX
        # produce "1.1.1.1, <ip real>". Recorrer la cadena al revés ignora lo
        # que el cliente injertó y devuelve efectivamente la IP real.
        for candidato in reversed(candidatos):
            # Los proxies de confianza intermedios se saltan; el primer valor
            # que no es un proxy conocido es el cliente.
            if not es_proxy_confiable(candidato):
                return normalizar(candidato)

        # La cadena sólo contiene proxies conocidos: no hay cliente
        # identificable. No se cae al peer porque sería la IP del NGINX, y
        # guardar el proxy como si fuera el cliente es un dato falso.
        return None

    return normalizar(x_real_ip) or normalizar(peer)


def get_client_ip(request: Request) -> Optional[str]:
    """Devuelve la IP real como string, o None si no se puede determinar."""
    peer = request.client.host if request.client else None
    return resolver_ip(
        peer,
        request.headers.get('x-forwarded-for'),
        request.headers.get('x-real-ip'),
    )
