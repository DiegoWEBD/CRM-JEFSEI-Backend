from datetime import datetime


class SolicitudCotizacion:
    def __init__(
        self, 
        id: int | None,
        fecha: datetime, 
        nombre_riesgo: str,
        informacion_completa: str,
        ejecutivo_comercial: str,
        prioridad: str, 
        observaciones: str | None,
        tipo: str,
        producto: str,
        recotizacion: bool
    ):
        self.id = id
        self.fecha = fecha
        self.prioridad = prioridad
        self.observaciones = observaciones
        self.tipo = tipo
        self.recotizacion = recotizacion
        self.nombre_riesgo = nombre_riesgo
        self.informacion_completa = informacion_completa
        self.ejecutivo_comercial = ejecutivo_comercial
        self.producto = producto