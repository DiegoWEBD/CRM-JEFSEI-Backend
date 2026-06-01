from datetime import datetime

from app.dominio.cotizacion.cotizacion import Cotizacion

class SolicitudCotizacion:
    def __init__(
        self, 
        fecha: datetime, 
        prioridad: str, 
        cotizaciones: list[Cotizacion],
        id: int | None = None
    ):
        self.id = id
        self.fecha = fecha
        self.prioridad = prioridad
        self.cotizaciones = cotizaciones