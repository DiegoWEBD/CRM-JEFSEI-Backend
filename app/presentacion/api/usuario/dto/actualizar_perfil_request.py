from pydantic import BaseModel, field_validator

from app.aplicacion.usuario.use_cases.actualizar_perfil import (
    LONGITUD_MAXIMA_NOMBRE,
    LONGITUD_MINIMA_NOMBRE,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException


class ActualizarPerfilRequest(BaseModel):
    """Self-service: el usuario actualiza su propio nombre de perfil."""

    nombre: str

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        v = v.strip()
        if not (LONGITUD_MINIMA_NOMBRE <= len(v) <= LONGITUD_MAXIMA_NOMBRE):
            raise DatoInvalidoException(
                f'El nombre debe tener entre {LONGITUD_MINIMA_NOMBRE} '
                f'y {LONGITUD_MAXIMA_NOMBRE} caracteres'
            )
        return v
