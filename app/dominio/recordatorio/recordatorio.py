from datetime import datetime, timezone


class Recordatorio:
    def __init__(
        self,
        id: int,
        id_prospecto: int | None,
        nombre_prospecto: str | None,
        titulo: str,
        detalle: str | None,
        completado: bool,
        tipo_gestion: str,
        prioridad: str,
        fecha_recordatorio: datetime
    ):
        self.id_prospecto = id_prospecto
        self.nombre_prospecto = nombre_prospecto
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