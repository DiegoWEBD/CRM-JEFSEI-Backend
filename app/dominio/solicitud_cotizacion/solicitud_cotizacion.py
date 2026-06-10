from datetime import datetime


class SolicitudCotizacion:
    def __init__(
        self, 
        fecha: datetime, 
        prioridad: str, 
        observaciones: str | None,
        tipo: str,
        id: int | None = None
    ):
        self.id = id
        self.fecha = fecha
        self.prioridad = prioridad
        self.observaciones = observaciones
        self.tipo = tipo