from typing import Literal

from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import SolicitudCotizacionRequest


class SolicitudCotizacionVidaGuardiaRequest(SolicitudCotizacionRequest):
    tipo: Literal['vida_guardia'] # type: ignore
    numero_guardias: int