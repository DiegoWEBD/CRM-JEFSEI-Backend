from datetime import datetime

from pydantic import BaseModel


class RegistrarComunicadoRequest(BaseModel):
    titulo: str
    descripcion: str
    prioridad: str
    caducidad: datetime
