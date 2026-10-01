from datetime import datetime, timezone


class RegistroAuditoria:

    def __init__(
        self,
        categoria: str,
        evento: str,
        resultado: str,
        ip_origen: str,
        estado_http: int | None = None,
        rut_usuario: str | None = None,
        nombre_usuario: str | None = None,
        user_agent: str | None = None,
        id_peticion: str | None = None,
        metodo: str | None = None,
        ruta: str | None = None,
        entidad_tipo: str | None = None,
        entidad_id: str | None = None,
        detalle: str | None = None,
        duracion_ms: int | None = None,
        fecha_registro: datetime | None = None,
        id: int | None = None,
    ):
        self.id = id
        self.categoria = categoria
        self.evento = evento
        self.resultado = resultado
        self.estado_http = estado_http
        self.rut_usuario = rut_usuario
        self.nombre_usuario = nombre_usuario
        self.ip_origen = ip_origen
        self.user_agent = user_agent
        self.id_peticion = id_peticion
        self.metodo = metodo
        self.ruta = ruta
        self.entidad_tipo = entidad_tipo
        self.entidad_id = entidad_id
        self.detalle = detalle
        self.duracion_ms = duracion_ms
        # El default no puede ser datetime.now(...) en la firma: se evaluaría una
        # sola vez al importar el módulo y todos los registros compartirían la
        # misma marca de tiempo.
        self.fecha_registro = (
            fecha_registro if fecha_registro is not None
            else datetime.now(tz=timezone.utc)
        )
