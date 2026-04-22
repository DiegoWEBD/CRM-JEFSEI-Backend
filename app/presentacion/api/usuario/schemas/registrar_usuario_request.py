from pydantic import BaseModel


class RegistrarUsuarioRequest(BaseModel):
    rut: str
    nombre: str
    correo: str
    telefono: str
    id_sucursal: int
    password: str
    codigo_roles: list[str]