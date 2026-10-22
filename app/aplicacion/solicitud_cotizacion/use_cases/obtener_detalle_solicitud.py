from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.usuario.usuario import Usuario


class ObtenerDetalleSolicitudUseCase:
    
    def __init__(
        self, 
        repositorio_solicitudes: RepositorioSolicitudesCotizacion,
        authorization_service: AuthorizationService
    ):
        self.repositorio_solicitudes = repositorio_solicitudes
        self.authorization_service = authorization_service

    def ejecutar(self, id: int, usuario: Usuario) -> SolicitudCotizacion:
        solicitud = self.repositorio_solicitudes.buscar(id)

        if not solicitud:
            raise RecursoNoEncontradoException(f'Solicitud {id} no encontrada')

        if not self.authorization_service.usuario_puede_ver_solicitud_cotizacion(usuario.rut, id):
            raise UsuarioNoAutorizadoException

        return solicitud