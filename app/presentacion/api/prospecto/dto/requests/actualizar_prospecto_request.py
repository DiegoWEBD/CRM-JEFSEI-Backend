from pydantic import BaseModel


class ActualizarProspectoRequest(BaseModel):
    rut_riesgo: str | None
    nombre_riesgo: str
    telefono_contacto: str | None
    correo_contacto: str | None
    direccion: str | None
    region: str | None
    comuna: str | None
    observaciones: str | None
