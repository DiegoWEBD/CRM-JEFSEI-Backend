from pydantic import BaseModel


class ActualizarTransicionRequest(BaseModel):
    es_manual: bool
    accion_requerida: str | None = None
