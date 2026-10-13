from pydantic import BaseModel


class ActualizarTransicionRequest(BaseModel):
    es_manual: bool
    accion_requerida: str | None = None
    # Solo aplica a la transición principal (SLA); en las secundarias se ignora.
    dias_limite: int | None = None
