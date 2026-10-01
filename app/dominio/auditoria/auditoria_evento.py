from datetime import datetime
from typing import Any, Optional

from app.dominio.auditoria.enums import Categoria, Resultado, TipoEvento


class AuditoriaEvento:
    """Registro inmutable de una acción. Solo se crea; nunca se modifica."""

    def __init__(
        self,
        id: int | None,
        fecha_hora: datetime | None,
        rut_usuario: str | None,
        tipo_evento: TipoEvento,
        categoria: Categoria,
        resultado: Resultado,
        request_id: str,
        metodo_http: str | None = None,
        endpoint: str | None = None,
        path: str | None = None,
        ip_origen: str | None = None,
        user_agent: str | None = None,
        origin: str | None = None,
        referer: str | None = None,
        id_sesion: str | None = None,
        recurso_tipo: str | None = None,
        recurso_id: str | None = None,
        descripcion: str | None = None,
        datos_antes: dict[str, Any] | None = None,
        datos_despues: dict[str, Any] | None = None,
        cambios: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        duracion_ms: int | None = None,
        status_http: int | None = None,
        error_codigo: str | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.fecha_hora = fecha_hora
        self.rut_usuario = rut_usuario
        self.tipo_evento = tipo_evento
        self.categoria = categoria
        self.resultado = resultado
        self.request_id = request_id
        self.metodo_http = metodo_http
        self.endpoint = endpoint
        self.path = path
        self.ip_origen = ip_origen
        self.user_agent = user_agent
        self.origin = origin
        self.referer = referer
        self.id_sesion = id_sesion
        self.recurso_tipo = recurso_tipo
        self.recurso_id = recurso_id
        self.descripcion = descripcion
        self.datos_antes = datos_antes
        self.datos_despues = datos_despues
        self.cambios = cambios
        self.metadata = metadata
        self.duracion_ms = duracion_ms
        self.status_http = status_http
        self.error_codigo = error_codigo
        self.created_at = created_at
