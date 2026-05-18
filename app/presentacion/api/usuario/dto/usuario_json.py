from pydantic import BaseModel

from app.presentacion.api.rol.dto.rol_json import RolJson


class UsuarioJson(BaseModel):
    rut: str
    nombre: str
    correo: str
    telefono: str
    sucursal: str
    fecha_registro: str
    habilitado: bool
    eliminado: bool
    meta_mensual_uf: int | None
    roles: list[RolJson]