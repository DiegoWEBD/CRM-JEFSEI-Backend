from pydantic import BaseModel


class ActualizarTransicionRequest(BaseModel):
    es_manual: bool
    accion_requerida: str | None = None
    # Solo aplica a la transición principal (SLA); en las secundarias se ignora.
    dias_limite: int | None = None
    # Roles responsables de las alertas SLA por tipo de oportunidad. Solo
    # aplica a la transición principal (en las secundarias se rechazan):
    # None = sin cambios, [] = sin responsables para ese tipo.
    roles_responsables_nuevas: list[str] | None = None
    roles_responsables_renovacion: list[str] | None = None
