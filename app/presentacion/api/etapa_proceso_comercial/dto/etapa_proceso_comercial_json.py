from pydantic import BaseModel


class EtapaProcesoComercialJson(BaseModel):
    codigo: str
    nombre: str
    dias_limite: int | None