from pydantic import BaseModel

from app.presentacion.api.estudio_comercial.dto.estudio_comercial_condominio_json import EstudioComercialCondominioJson
from app.presentacion.api.historial_estado.dto.historial_estado_json import HistorialEstadoJson
from app.presentacion.api.solicitud_cotizacion.dto.solicitud_cotizacion_json import SolicitudCotizacionJson
from app.presentacion.api.usuario.dto.usuario_json_resumen import UsuarioJsonResumen


class ProcesoComercialJson(BaseModel):
    id: int
    historial_estados: list[HistorialEstadoJson] 
    ejecutivo_comercial: UsuarioJsonResumen | None
    ejecutivo_evaluacion: UsuarioJsonResumen | None
    solicitudes_cotizacion: list[SolicitudCotizacionJson]
    estudio: EstudioComercialCondominioJson | None
    #poliza: PolizaJ | None 
    #plan_pago: PlanPago | None
    