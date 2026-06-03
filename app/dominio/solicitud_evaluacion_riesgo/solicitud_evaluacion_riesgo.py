from datetime import datetime


class SolicitudEvaluacionRiesgo:

    def __init__(
        self,
        fecha_solicitud: datetime,
        prioridad: str,
        id: int | None = None
    ):
        self.id = id
        self.fecha_solicitud = fecha_solicitud
        self.prioridad = prioridad