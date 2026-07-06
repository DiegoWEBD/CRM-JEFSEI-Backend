from datetime import datetime

from pydantic import BaseModel


class GestionComercialJson(BaseModel):
    id: int
    tipo: str
    rut_usuario: str
    nombre_ejecutivo: str | None
    id_prospecto: int
    nombre_cliente: str | None
    titulo: str
    estado_contacto: str | None
    observacion: str | None
    created_at: datetime
    fecha_gestion: datetime
