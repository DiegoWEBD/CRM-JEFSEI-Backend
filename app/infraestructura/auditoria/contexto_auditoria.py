"""Contexto de auditoría construido desde la request (§12).

El endpoint nunca entrega rut, IP ni User-Agent a mano: el middleware arma este
objeto y el servicio de auditoría lee de acá. Si un dato no está, queda None y
se sigue: la auditoría nunca bloquea un request.
"""

from typing import Optional


class AuditContext:
    __slots__ = (
        'request_id',
        'rut_usuario',
        'id_sesion',
        'ip_origen',
        'user_agent',
        'device_id',
        'metodo_http',
        'endpoint',
        'path',
        'origin',
        'referer',
        'status_http',
        'duracion_ms',
        'metadata',
    )

    def __init__(
        self,
        request_id: str,
        rut_usuario: str | None = None,
        id_sesion: str | None = None,
        ip_origen: str | None = None,
        user_agent: str | None = None,
        device_id: str | None = None,
        metodo_http: str | None = None,
        endpoint: str | None = None,
        path: str | None = None,
        origin: str | None = None,
        referer: str | None = None,
        status_http: int | None = None,
        duracion_ms: int | None = None,
        metadata: dict | None = None,
    ):
        self.request_id = request_id
        self.rut_usuario = rut_usuario
        self.id_sesion = id_sesion
        self.ip_origen = ip_origen
        self.user_agent = user_agent
        self.device_id = device_id
        self.metodo_http = metodo_http
        self.endpoint = endpoint
        self.path = path
        self.origin = origin
        self.referer = referer
        self.status_http = status_http
        self.duracion_ms = duracion_ms
        self.metadata = metadata or {}

    def con(self, **cambios) -> 'AuditContext':
        """Copia con campos agregados. No muta el original."""
        estado = {campo: getattr(self, campo) for campo in self.__slots__}
        estado.update(cambios)
        return AuditContext(**estado)
