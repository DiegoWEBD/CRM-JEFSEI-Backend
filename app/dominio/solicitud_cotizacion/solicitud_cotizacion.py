from datetime import datetime



class SolicitudCotizacion:
    def __init__(
        self, 
        id: int | None,
        fecha: datetime, 
        nombre_riesgo: str,
        informacion_completa: bool,
        rut_ejecutivo_comercial: str,
        nombre_ejecutivo_comercial: str,
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
        self.rut_ejecutivo_comercial = rut_ejecutivo_comercial
        self.nombre_ejecutivo_comercial = nombre_ejecutivo_comercial
        self.producto = producto