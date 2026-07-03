import re

from pydantic import BaseModel, field_validator

from app.presentacion.api.usuario.dto.usuario_json import UsuarioJson

class IniciarSesionRequest(BaseModel):
    rut: str
    password: str

    @field_validator('rut')
    @classmethod
    def normalizar_rut(cls, v: str) -> str:
        clean = re.sub(r'[^0-9kK]', '', v).upper()
        if len(clean) <= 1:
            return clean
        return f"{clean[:-1]}-{clean[-1]}"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expire_minutes: int
    usuario: UsuarioJson