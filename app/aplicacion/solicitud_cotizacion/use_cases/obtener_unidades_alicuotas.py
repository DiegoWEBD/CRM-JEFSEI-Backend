from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota


class ObtenerUnidadesAlicuotasUseCase:

    def __init__(
        self,
        repositorio_solicitudes: RepositorioSolicitudesCotizacion,
        repositorio_unidades: RepositorioUnidadesAlicuotas,
        authorization_service: AuthorizationService,
    ) -> None:
        self.repositorio_solicitudes = repositorio_solicitudes
        self.repositorio_unidades = repositorio_unidades
        self.authorization_service = authorization_service

    def ejecutar(self, id_solicitud: int, rut_usuario: str | None) -> list[UnidadAlicuota]:
        solicitud = self.repositorio_solicitudes.buscar(id_solicitud)

        if not solicitud or not solicitud.id:
            raise RecursoNoEncontradoException('Solicitud no encontrada')

        if rut_usuario is not None and not self.authorization_service.usuario_puede_ver_solicitud_cotizacion(
            rut_usuario, solicitud.id
        ):
            raise UsuarioNoAutorizadoException

        return self.repositorio_unidades.listar_por_solicitud(id_solicitud)
