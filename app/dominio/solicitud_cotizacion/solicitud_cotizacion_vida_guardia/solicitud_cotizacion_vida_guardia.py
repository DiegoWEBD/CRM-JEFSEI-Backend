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
        motivo_recotizacion: str | None,
        numero_guardias: int,
        cantidad_cotizaciones: int = 0
    ):
        super().__init__(
            id=id,
            fecha=fecha,
            prioridad=prioridad,
            observaciones=observaciones,
            tipo=tipo,
            recotizacion=recotizacion,
            motivo_recotizacion=motivo_recotizacion,
            nombre_riesgo=nombre_riesgo,
            informacion_completa=informacion_completa,
            rut_ejecutivo_comercial=rut_ejecutivo_comercial,
            nombre_ejecutivo_comercial=nombre_ejecutivo_comercial,
            producto=producto,
            cantidad_cotizaciones=cantidad_cotizaciones
        )

        self.numero_guardias = numero_guardias
        