from datetime import datetime, timezone


class Recordatorio:
    def __init__(
        self,
        id: int,
        titulo: str,
        detalle: str | None,
        completado: bool,
        tipo_gestion: str,
        prioridad: str,
        fecha_recordatorio: datetime
    ):
        self.titulo = titulo
        self.detalle = detalle
        self.completado = completado
        self.tipo_gestion = tipo_gestion
        self.prioridad = prioridad
        self.fecha_recordatorio = fecha_recordatorio
        self.id = id
        
        if completado:
            self.estado = 'completado'

        now = datetime.now(timezone.utc)

        if fecha_recordatorio > now:
            self.estado = 'pendiente'
        else:
            self.estado = 'atrasado'