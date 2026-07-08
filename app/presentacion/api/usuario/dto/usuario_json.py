from pydantic import BaseModel

from app.presentacion.api.rol.dto.rol_json import RolJson


class UsuarioJson(BaseModel):
    rut: str
    nombre: str
    correo: str | None = None
    telefono: str | None = None
    sucursal: str
    fecha_registro: str
    habilitado: bool
    eliminado: bool
    meta_mensual_uf: int | None
    porcentaje_comision: float | None
    roles: list[RolJson]