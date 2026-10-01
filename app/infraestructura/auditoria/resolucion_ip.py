from app.core.config import settings


def resolver_ip_origen(headers, client_host: str | None) -> str:
    """Resuelve la IP real del cliente.

    El tráfico llega al backend desde el BFF (Next.js), por lo que la IP del
    peer directo no es la del usuario. Solo se confía en los headers de proxy
    cuando el peer directo está en CRM_PROXY_CONFIABLES.
    """
    if client_host in settings.proxies_confiables:
        forwarded = headers.get('x-forwarded-for')
        if forwarded:
            primera_ip = forwarded.split(',')[0].strip()
            if primera_ip:
                return primera_ip

        ip_real = headers.get('x-real-ip')
        if ip_real and ip_real.strip():
            return ip_real.strip()

    return client_host or 'desconocida'
