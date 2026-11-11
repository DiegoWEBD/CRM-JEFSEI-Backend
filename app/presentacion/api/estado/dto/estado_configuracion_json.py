from pydantic import BaseModel


class EstadoConfiguracionJson(BaseModel):
    codigo: str
    nombre: str
    codigo_etapa: str
    nombre_etapa: str
    probabilidad_cierre: float
    cantidad_transiciones: int
