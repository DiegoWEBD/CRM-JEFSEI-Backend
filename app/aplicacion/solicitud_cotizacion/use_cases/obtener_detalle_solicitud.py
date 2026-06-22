from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.usuario.usuario import Usuario


class ObtenerDetalleSolicitudUseCase:
    
    def __init__(
        self, 
        repositorio_solicitudes: RepositorioSolicitudesCotizacion
    ):
        self.repositorio_solicitudes = repositorio_solicitudes

    def ejecutar(self, id: int, usuario: Usuario) -> SolicitudCotizacion:
        solicitud = self.repositorio_solicitudes.buscar(id)

        if not solicitud:
            raise RecursoNoEncontradoException(f'Solicitud {id} no encontrada')

        return solicitud