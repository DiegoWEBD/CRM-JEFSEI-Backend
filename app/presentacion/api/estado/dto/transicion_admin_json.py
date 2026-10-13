from pydantic import BaseModel


class TransicionAdminJson(BaseModel):
    codigo_estado_origen: str
    codigo_estado_destino: str
    nombre_estado_origen: str | None
    nombre_estado_destino: str
    es_manual: bool
    es_principal: bool
    accion_requerida: str | None
