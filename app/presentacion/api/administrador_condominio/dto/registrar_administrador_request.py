from pydantic import BaseModel


class RegistrarAdministradorRequest(BaseModel):
    nombre_administrador: str
    nombre_contacto: str | None = None
    telefono: str | None = None
    correo: str | None = None
