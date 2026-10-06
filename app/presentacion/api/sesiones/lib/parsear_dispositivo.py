import re


_PATRONES_NAVEGADOR: list[tuple[str, str]] = [
    (r'Edg(?:e|A|iOS)?/([\d.]+)', 'Edge'),
    (r'OPR/([\d.]+)', 'Opera'),
    (r'Chrome/([\d.]+)', 'Chrome'),
    (r'Firefox/([\d.]+)', 'Firefox'),
    (r'Version/([\d.]+).*Safari', 'Safari'),
    (r'Safari', 'Safari'),
]

_PATRONES_SO: list[tuple[str, str]] = [
    (r'Windows NT 10\.0', 'Windows 10'),
    (r'Windows NT 6\.3', 'Windows 8.1'),
    (r'Windows NT 6\.2', 'Windows 8'),
    (r'Windows NT 6\.1', 'Windows 7'),
    (r'Windows', 'Windows'),
    (r'Mac OS X ([\d_]+)', 'macOS'),
    (r'iPhone|iPad', 'iOS'),
    (r'Android ([\d.]+)', 'Android'),
    (r'Linux', 'Linux'),
]


def parsear_dispositivo(user_agent: str | None) -> str | None:
    """Extrae un string legible del user-agent.

    Retorna algo como ``"Chrome 120 · Windows 10"`` o ``None`` si no se
    puede determinar.
    """
    if not user_agent:
        return None

    navegador: str | None = None
    for patron, nombre in _PATRONES_NAVEGADOR:
        match = re.search(patron, user_agent)
        if match:
            version = match.group(1) if match.lastindex else ''
            # Solo la parte mayor de la versión
            mayor = version.split('.')[0] if version else ''
            navegador = f'{nombre} {mayor}' if mayor else nombre
            break

    so: str | None = None
    for patron, nombre in _PATRONES_SO:
        match = re.search(patron, user_agent)
        if match:
            if nombre == 'macOS' and match.lastindex:
                version = match.group(1).replace('_', '.')
                so = f'macOS {version}'
            else:
                so = nombre
            break

    if navegador and so:
        return f'{navegador} · {so}'
    return navegador or so