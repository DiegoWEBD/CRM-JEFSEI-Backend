from pydantic import BaseModel, ConfigDict


class UsuarioJson(BaseModel):
    rut: str
    nombre: str
    correo: str
    telefono: str
    sucursal: str
    roles: list[str]