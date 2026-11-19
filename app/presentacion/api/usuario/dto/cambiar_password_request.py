from pydantic import BaseModel, field_validator

from app.dominio.usuario.validar_password import validar_fortaleza_password


class CambiarPasswordRequest(BaseModel):
    """Self-service: el usuario cambia su propia contraseña.

    Exige la contraseña actual; la nueva debe cumplir la política de fortaleza.
    """

    password_actual: str
    password_nueva: str

    @field_validator('password_nueva')
    @classmethod
    def validar_password_nueva(cls, v: str) -> str:
        validar_fortaleza_password(v)
        return v
