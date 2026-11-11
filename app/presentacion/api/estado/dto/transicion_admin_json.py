from pydantic import BaseModel


class TransicionAdminJson(BaseModel):
    codigo_estado_origen: str
    codigo_estado_destino: str
    nombre_estado_origen: str | None
    nombre_estado_destino: str
    es_manual: bool
    es_principal: bool
    accion_requerida: str | None
    # SLA de permanencia: solo en la transición principal (NULL en secundarias).
    dias_limite: int | None
    # Roles responsables de las alertas SLA, por tipo de oportunidad:
    # solo en la transición principal (vacíos en secundarias).
    roles_responsables_nuevas: list[str] = []
    roles_responsables_renovacion: list[str] = []
