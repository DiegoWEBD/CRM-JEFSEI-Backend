from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class SesionConUsuario:
    """Datos de una sesión con el nombre del usuario asociado.

    Se usa para la vista de administración de sesiones, donde se necesita
    mostrar el nombre del usuario sin hacer un JOIN adicional en el cliente.
    """

    id: UUID
    rut_usuario: str
    nombre_usuario: str | None
    ip: str | None
    user_agent: str | None
    creado_en: datetime
    expira_en: datetime
    ultimo_acceso: datetime | None
    revocado_en: datetime | None
    motivo_revocacion: str | None