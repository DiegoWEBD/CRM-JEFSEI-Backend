from pydantic import BaseModel


class EstadoConfiguracionJson(BaseModel):
    codigo: str
    nombre: str
    codigo_etapa: str
    nombre_etapa: str
    probabilidad_cierre: float
    dias_limite: int | None
    rol_responsable: str | None
    nombre_rol_responsable: str | None
    cantidad_transiciones: int
