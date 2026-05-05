from pydantic import BaseModel

from app.presentacion.api.usuario.dto.usuario_json import UsuarioJson

class IniciarSesionRequest(BaseModel):
    rut: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expire_minutes: int
    usuario: UsuarioJson