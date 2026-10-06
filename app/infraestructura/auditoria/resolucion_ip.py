import ipaddress

from app.core.config import settings


def _es_proxy_confiable(client_host: str, proxies: list[str]) -> bool:
    """Verifica si el peer directo está en la lista de proxies confiables.

    Cada entrada de proxies puede ser una IP exacta (127.0.0.1, ::1) o un
    rango CIDR (172.19.0.0/16). El rango CIDR permite confiar en toda la red
    Docker sin depender de IPs de contenedores que pueden cambiar.
    """
    try:
        ip = ipaddress.ip_address(client_host)
    except ValueError:
        return False

    for proxy in proxies:
        try:
            red = ipaddress.ip_network(proxy, strict=False)
        except ValueError:
            continue
        if ip in red:
            return True
    return False


def resolver_ip_origen(headers, client_host: str | None) -> str:
    """Resuelve la IP real del cliente.

    El tráfico llega al backend desde el BFF (Next.js), por lo que la IP del
    peer directo no es la del usuario. Solo se confía en los headers de proxy
    cuando el peer directo está en CRM_PROXY_CONFIABLES.
    """
    if client_host and _es_proxy_confiable(client_host, settings.proxies_confiables):
        forwarded = headers.get('x-forwarded-for')
        if forwarded:
            primera_ip = forwarded.split(',')[0].strip()
            if primera_ip:
                return primera_ip

        ip_real = headers.get('x-real-ip')
        if ip_real and ip_real.strip():
            return ip_real.strip()

    return client_host or 'desconocida'
