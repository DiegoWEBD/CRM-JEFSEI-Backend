from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.estudio_comercial.estudio_comercial_condominio.estudio_comercial_condominio import EstudioComercialCondominio
from app.dominio.estudio_comercial.estudio_comercial_condominio.repositorio_estudios_comerciales import RepositorioEstudiosComerciales
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.usuario.usuario import Usuario


class ListarEstudiosComercialesUseCase:
    def __init__(
        self,
        repositorio_solicitudes: RepositorioSolicitudesCotizacion,
        repositorio_estudios: RepositorioEstudiosComerciales,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_estudios = repositorio_estudios
        self.repositorio_solicitudes = repositorio_solicitudes
        self.authorization_service = authorization_service

    def ejecutar(self, id_solicitud: int, usuario: Usuario) -> list[EstudioComercialCondominio]:

        if not self.repositorio_solicitudes.buscar(id_solicitud):
            raise RecursoNoEncontradoException("Solicitud no encontrada")

        if not self.authorization_service.usuario_puede_ver_estudios_comerciales(usuario.rut, id_solicitud):
            raise UsuarioNoAutorizadoException
    
        return self.repositorio_estudios.listar_por_id_solicitud(id_solicitud)