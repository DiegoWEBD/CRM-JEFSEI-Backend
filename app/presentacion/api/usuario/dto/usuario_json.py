from pydantic import BaseModel


class UsuarioJson(BaseModel):
    rut: str
    nombre: str
    correo: str
    telefono: str
    sucursal: str
    meta_mensual_uf: int | None
    roles: list[str]