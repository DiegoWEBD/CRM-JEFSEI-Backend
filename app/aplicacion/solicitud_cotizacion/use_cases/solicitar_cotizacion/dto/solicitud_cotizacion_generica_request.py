from typing import Literal

from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_request import SolicitudCotizacionRequest


class SolicitudCotizacionGenericaRequest(SolicitudCotizacionRequest):
    tipo: Literal[ # type: ignore
        'vehiculos',
        'hogar',
        'vida',
        'salud_complementario',
        'mascotas',
        'espacios_comunes'
    ]