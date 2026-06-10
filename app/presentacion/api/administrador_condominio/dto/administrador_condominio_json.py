from pydantic import BaseModel


class AdministradorCondominioJson(BaseModel):
    id: int | None
    nombre_administrador: str
    nombre_contacto: str | None
    telefono: str | None
    correo: str | None