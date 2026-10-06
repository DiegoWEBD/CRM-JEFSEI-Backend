from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SesionJson(BaseModel):
    id: UUID
    rut_usuario: str
    nombre_usuario: str | None
    ip: str | None
    user_agent: str | None
    dispositivo: str | None
    creado_en: datetime
    ultimo_acceso: datetime | None
    duracion_minutos: float | None
    esta_activa: bool
    revocado_en: datetime | None
    motivo_revocacion: str | None