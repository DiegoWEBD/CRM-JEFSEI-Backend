from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.infraestructura.cotizacion.adaptadores.cotizacion_json_adapter import CotizacionJsonAdapter
from app.presentacion.api.solicitud_cotizacion.dto.solicitud_cotizacion_json import SolicitudCotizacionJson


class SolicitudCotizacionJsonAdapter:
    def __init__(self, solicitud_cotizacion: SolicitudCotizacion):
        self.solicitud_cotizacion = solicitud_cotizacion

    def to_json(self) -> SolicitudCotizacionJson:
        if not self.solicitud_cotizacion.id:
            raise Exception('Solicitud de Cotización inválida')
        
        return SolicitudCotizacionJson(
            id=self.solicitud_cotizacion.id,
            fecha=self.solicitud_cotizacion.fecha.isoformat(),
            prioridad=self.solicitud_cotizacion.prioridad,
            cotizaciones=[CotizacionJsonAdapter(cotizacion).to_cotizacion_json() for cotizacion in self.solicitud_cotizacion.cotizaciones]
        )