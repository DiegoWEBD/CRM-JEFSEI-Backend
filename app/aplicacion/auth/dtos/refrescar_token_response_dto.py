from dataclasses import dataclass
from app.dominio.usuario.usuario import Usuario


@dataclass
class RefrescarTokenResponseDTO:
    access_token: str
    refresh_token: str
    usuario: Usuario
    expire_minutes: int
    token_type: str = 'bearer'
