from datetime import datetime, timezone
from typing import Optional


class Sesion:
    """Sesión autenticada persistida.

    Existía únicamente como JWT sin estado: no se podía revocar ni expirar de
    forma verificable. Con esta tabla la revocación es real y auditable.
    """

    def __init__(
        self,
        id: str,
        rut_usuario: str,
        fecha_creacion: datetime | None,
        fecha_expiracion: datetime,
        fecha_ultimo_uso: datetime | None = None,
        revocada: bool = False,
        fecha_revocacion: datetime | None = None,
        motivo_revocacion: str | None = None,
        ip_origen: str | None = None,
        user_agent: str | None = None,
        device_id: str | None = None,
    ):
        self.id = id
        self.rut_usuario = rut_usuario
        self.fecha_creacion = fecha_creacion
        self.fecha_expiracion = fecha_expiracion
        self.fecha_ultimo_uso = fecha_ultimo_uso
        self.revocada = revocada
        self.fecha_revocacion = fecha_revocacion
        self.motivo_revocacion = motivo_revocacion
        self.ip_origen = ip_origen
        self.user_agent = user_agent
        self.device_id = device_id

    def esta_vencida(self, ahora: datetime) -> bool:
        return self.fecha_expiracion <= ahora

    def esta_vencida_ahora(self) -> bool:
        return self.esta_vencida(datetime.now(timezone.utc))

    def esta_revocada(self) -> bool:
        return self.revocada
