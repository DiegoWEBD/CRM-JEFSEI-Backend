from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.usuario.usuario import Usuario


class ObtenerSolicitudesCotizacionUseCase:
    
    def __init__(
        self, 
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
        repositorio_solicitudes: RepositorioSolicitudesCotizacion,
        authorization_service: AuthorizationService
    ):
        self.repositorio_solicitudes = repositorio_solicitudes
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales
        self.authorization_service = authorization_service

    def ejecutar(self, id_proceso_comercial: int, usuario: Usuario) -> list[SolicitudCotizacion]:
        if not self.repositorio_procesos_comerciales.buscar(id_proceso_comercial):
            raise RecursoNoEncontradoException('Oportunidad no encontrada')

        if not self.authorization_service.usuario_puede_ver_solicitudes_cotizacion(usuario, id_proceso_comercial):
            raise UsuarioNoAutorizadoException

        return self.repositorio_solicitudes.obtener_solicitudes(id_proceso_comercial)