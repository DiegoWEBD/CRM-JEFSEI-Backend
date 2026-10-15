from datetime import datetime, timezone


class HistorialEstadoProcesoComercial:
    def __init__(
        self,
        id_proceso_comercial: int,
        codigo_estado: str,
        rut_registrado_por: str,
        fecha: datetime = datetime.now(tz=timezone.utc),
        observacion: str | None = None,
    ):
        self.id_proceso_comercial = id_proceso_comercial
        self.codigo_estado = codigo_estado
        self.rut_registrado_por = rut_registrado_por
        self.fecha = fecha
        self.observacion = observacion