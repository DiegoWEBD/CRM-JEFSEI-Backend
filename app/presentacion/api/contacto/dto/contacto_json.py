from pydantic import BaseModel


class ContactoJson(BaseModel):
    id: int
    id_prospecto: int
    nombre: str
    telefono: str | None
    correo: str | None
    cargo: str | None