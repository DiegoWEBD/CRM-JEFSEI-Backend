from pydantic import BaseModel


class FiltrosSesiones(BaseModel):
    rut_usuario: str | None = None
    estado: str | None = None