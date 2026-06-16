from typing import Literal

from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import SolicitudCotizacionRequest


class SolicitudCotizacionUnidadesRequest(SolicitudCotizacionRequest):
    tipo: Literal['unidades'] # type: ignore
    monto_asegurado_total: float
    nombre_excel: str