from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion


class ObtenerSolicitudesCotizacionActivasUseCase:
    
    def __init__(
        self, 
        repositorio_solicitudes: RepositorioSolicitudesCotizacion
    ):
        self.repositorio_solicitudes = repositorio_solicitudes

    def ejecutar(self, id_prospecto: int) -> list[SolicitudCotizacion]:
        return self.repositorio_solicitudes.obtener_solicitudes_activas(id_prospecto)