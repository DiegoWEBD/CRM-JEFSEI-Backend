from pydantic import BaseModel


class EstadoInformativoJson(BaseModel):
    codigo: str 
    nombre: str
    fecha_registro: str