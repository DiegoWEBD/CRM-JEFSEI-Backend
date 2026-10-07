from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Sesion:
    id: UUID
    rut_usuario: str
    ip: str | None
    user_agent: str | None
    creado_en: datetime
    expira_en: datetime
    ultimo_acceso: datetime | None
    revocado_en: datetime | None
    motivo_revocacion: str | None

    @property
    def esta_vigente(self) -> bool:
        return self.revocado_en is None and self.expira_en > datetime.now(self.expira_en.tzinfo)
