from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota


class ObtenerUnidadesAlicuotasUseCase:

    def __init__(
        self,
        repositorio_unidades: RepositorioUnidadesAlicuotas,
        authorization_service: AuthorizationService,
    ) -> None:
        self.repositorio_unidades = repositorio_unidades
        self.authorization_service = authorization_service

    def ejecutar(self, id_solicitud: int, rut_usuario: str | None) -> list[UnidadAlicuota]:
        """`rut_usuario` es None cuando el usuario tiene permiso global."""

        if rut_usuario is not None and not self.authorization_service.usuario_puede_ver_solicitud_cotizacion(
            rut_usuario, id_solicitud
        ):
            raise UsuarioNoAutorizadoException

        return self.repositorio_unidades.listar_por_solicitud(id_solicitud)
