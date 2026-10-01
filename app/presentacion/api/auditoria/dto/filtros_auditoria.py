from datetime import datetime

from pydantic import BaseModel


class FiltrosAuditoria(BaseModel):
    categoria: str | None = None
    evento: str | None = None
    rut_usuario: str | None = None
    ip_origen: str | None = None
    entidad_tipo: str | None = None
    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None
    texto_busqueda: str | None = None
