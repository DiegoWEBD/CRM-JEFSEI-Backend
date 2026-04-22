from pydantic import BaseModel

class IniciarSesionRequest(BaseModel):
    rut: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"