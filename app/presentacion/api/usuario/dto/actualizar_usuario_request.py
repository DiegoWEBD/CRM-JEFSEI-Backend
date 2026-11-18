import re

from pydantic import BaseModel, field_validator

from app.dominio.usuario.validar_password import validar_fortaleza_password


class ActualizarUsuarioRequest(BaseModel):
    rut: str
    nombre: str
    correo: str | None
    telefono: str | None
    id_sucursal: int
    password: str | None = None
    meta_mensual_uf: int | None
    codigo_roles: list[str]
    porcentaje_comision: float | None
    habilitado: bool

    @field_validator('password')
    @classmethod
    def validar_password(cls, v: str | None) -> str | None:
        # Vacío o None significa "mantener la contraseña actual"
        if not v:
            return v
        validar_fortaleza_password(v)
        return v

    @field_validator('rut')
    @classmethod
    def normalizar_rut(cls, v: str) -> str:
        clean = re.sub(r'[^0-9kK]', '', v).upper()
        if len(clean) <= 1:
            return clean
        return f"{clean[:-1]}-{clean[-1]}"
