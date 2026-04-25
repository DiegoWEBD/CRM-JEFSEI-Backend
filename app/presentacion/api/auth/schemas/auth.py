from pydantic import BaseModel

from app.presentacion.api.usuario.schemas.usuario_json import UsuarioJson

class IniciarSesionRequest(BaseModel):
    rut: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioJson