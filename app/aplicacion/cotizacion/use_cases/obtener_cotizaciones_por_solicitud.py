from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.cotizacion.repositorio_cotizaciones import RepositorioCotizaciones
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion


class ObtenerCotizacionesPorSolicitudUseCase:

    def __init__(
        self, 
        repositorio_solicitudes_cotizacion: RepositorioSolicitudesCotizacion,
        repositorio_cotizaciones: RepositorioCotizaciones,
        authorization_service: AuthorizationService
    ) -> None:
        self.repositorio_cotizaciones = repositorio_cotizaciones
        self.authorization_service = authorization_service
        self.repositorio_solicitudes_cotizacion = repositorio_solicitudes_cotizacion

    def ejecutar(self, id_solicitud: int, rut_usuario: str | None) -> list[Cotizacion]:

        if not self.repositorio_solicitudes_cotizacion.existe_solicitud(id_solicitud):
            raise RecursoNoEncontradoException('Solicitud no encontrada')

        if rut_usuario and not self.authorization_service.usuario_puede_ver_solicitud_cotizacion(rut_usuario, id_solicitud):
            raise UsuarioNoAutorizadoException

        return self.repositorio_cotizaciones.obtener_por_solicitud(id_solicitud)