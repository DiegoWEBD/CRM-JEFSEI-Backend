from pydantic import BaseModel


class CrearTransicionRequest(BaseModel):
    codigo_estado_destino: str
    es_manual: bool = True
    es_principal: bool = False
    accion_requerida: str | None = None
