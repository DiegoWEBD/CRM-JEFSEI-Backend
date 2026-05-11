from pydantic import BaseModel

from app.presentacion.api.rol.dto.rol_json import RolJson


class UsuarioJsonResumen(BaseModel):
    rut: str
    nombre: str