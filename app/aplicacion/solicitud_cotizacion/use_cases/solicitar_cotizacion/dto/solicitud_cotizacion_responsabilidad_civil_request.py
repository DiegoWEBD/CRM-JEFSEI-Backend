from typing import Literal

from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import SolicitudCotizacionRequest


class SolicitudCotizacionResponsabilidadCivilRequest(SolicitudCotizacionRequest):
    tipo: Literal['rc_condominio'] # type: ignore
    actividad_del_condominio: str
    limite: float