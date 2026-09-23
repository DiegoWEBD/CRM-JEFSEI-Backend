from datetime import datetime


class Notificacion:

    def __init__(
        self,
        id: int | None,
        rut_usuario: str,
        codigo_tipo: str,
        nivel: str,
        titulo: str,
        mensaje: str,
        entidad_tipo: str | None,
        entidad_id: int | None,
        url_destino: str | None,
        dedupe_key: str,
        leida: bool,
        fecha_leida: datetime | None,
        created_at: datetime | None,
    ):
        self.id = id
        self.rut_usuario = rut_usuario
        self.codigo_tipo = codigo_tipo
        self.nivel = nivel
        self.titulo = titulo
        self.mensaje = mensaje
        self.entidad_tipo = entidad_tipo
        self.entidad_id = entidad_id
        self.url_destino = url_destino
        self.dedupe_key = dedupe_key
        self.leida = leida
        self.fecha_leida = fecha_leida
        self.created_at = created_at
