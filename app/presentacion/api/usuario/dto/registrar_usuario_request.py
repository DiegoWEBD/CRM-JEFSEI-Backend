from pydantic import BaseModel


class RegistrarUsuarioRequest(BaseModel):
    rut: str
    nombre: str
    correo: str
    telefono: str
    id_sucursal: int
    password: str
    meta_mensual_uf: int | None
    codigo_roles: list[str]
    porcentaje_comision: float | None
    junior: bool