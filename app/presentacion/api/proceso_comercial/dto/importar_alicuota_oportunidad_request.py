from pydantic import BaseModel


class UnidadAlicuotaRequest(BaseModel):
    identificador_unidad: str
    prorrateo: float
    fila_origen: int


class ImportarAlicuotaOportunidadRequest(BaseModel):
    nombre_excel: str
    unidades: list[UnidadAlicuotaRequest]
