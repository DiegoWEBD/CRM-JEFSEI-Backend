from pydantic import BaseModel

from app.presentacion.api.rol.dto.rol_json import RolJson


class UsuarioJson(BaseModel):
    rut: str
    nombre: str
    correo: str
    telefono: str
    sucursal: str
    meta_mensual_uf: int | None
    roles: list[RolJson]