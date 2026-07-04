from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from datetime import datetime


class SolicitudCotizacionResponsabilidadCivil(SolicitudCotizacion):
    
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
        actividad_del_condominio: str,
        limite: float,
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

        self.limite = limite
        self.actividad_del_condominio = actividad_del_condominio
        