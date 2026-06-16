from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from datetime import datetime


class SolicitudCotizacionVidaGuardia(SolicitudCotizacion):
    
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
        recotizacion: bool,
        numero_guardias: int
    ):
        super().__init__(
            id=id,
            fecha=fecha,
            prioridad=prioridad,
            observaciones=observaciones,
            tipo=tipo,
            recotizacion=recotizacion,
            nombre_riesgo=nombre_riesgo,
            informacion_completa=informacion_completa,
            rut_ejecutivo_comercial=rut_ejecutivo_comercial,
            nombre_ejecutivo_comercial=nombre_ejecutivo_comercial,
            producto=producto
        )

        self.numero_guardias = numero_guardias
        