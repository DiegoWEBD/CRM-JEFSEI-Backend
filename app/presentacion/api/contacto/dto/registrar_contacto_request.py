from pydantic import BaseModel


class RegistrarContactoRequest(BaseModel):
    nombre: str
    telefono: str | None = None
    correo: str | None = None
    cargo: str | None = None