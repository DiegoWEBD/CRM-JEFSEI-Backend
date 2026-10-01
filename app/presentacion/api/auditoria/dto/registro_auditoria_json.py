from datetime import datetime

from pydantic import BaseModel


class RegistroAuditoriaJson(BaseModel):
    id: int
    fecha_registro: datetime
    categoria: str
    evento: str
    resultado: str
    estado_http: int | None
    rut_usuario: str | None
    nombre_usuario: str | None
    ip_origen: str
    user_agent: str | None
    id_peticion: str | None
    metodo: str | None
    ruta: str | None
    entidad_tipo: str | None
    entidad_id: str | None
    detalle: str | None
    duracion_ms: int | None
