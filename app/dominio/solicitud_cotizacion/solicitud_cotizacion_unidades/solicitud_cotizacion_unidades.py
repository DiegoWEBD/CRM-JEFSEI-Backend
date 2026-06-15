from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from datetime import datetime


class SolicitudCotizacionUnidades(SolicitudCotizacion):
    
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
        recotizacion: bool,
        monto_asegurado_total: float,
        nombre_excel: str
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
            ejecutivo_comercial=ejecutivo_comercial,
            producto=producto
        )

        self.monto_asegurado_total = monto_asegurado_total
        self.nombre_excel = nombre_excel
        