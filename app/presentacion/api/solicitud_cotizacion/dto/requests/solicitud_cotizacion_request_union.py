from typing import Annotated

from pydantic import Field

from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_accidentes_personales_request.solicitud_cotizacion_accidentes_personales_request import SolicitudCotizacionAccidentesPersonalesRequest
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_generica_request import SolicitudCotizacionGenericaRequest
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_responsabilidad_civil_request import SolicitudCotizacionResponsabilidadCivilRequest
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_unidades_request import SolicitudCotizacionUnidadesRequest
from app.aplicacion.solicitud_cotizacion.use_cases.solicitar_cotizacion.dto.solicitud_cotizacion_vida_guardia_request import SolicitudCotizacionVidaGuardiaRequest

SolicitudCotizacionRequestUnion = Annotated[
    (
        SolicitudCotizacionGenericaRequest
        | SolicitudCotizacionVidaGuardiaRequest
        | SolicitudCotizacionUnidadesRequest
        | SolicitudCotizacionAccidentesPersonalesRequest
        | SolicitudCotizacionResponsabilidadCivilRequest
    ),
    Field(discriminator='tipo'),
]