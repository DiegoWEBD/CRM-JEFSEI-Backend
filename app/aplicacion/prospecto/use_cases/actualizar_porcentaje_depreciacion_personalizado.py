from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario


class ActualizarPorcentajeDepreciacionPersonalizadoUseCase:

    def __init__(
        self,
        repositorio_prospectos: RepositorioProspectos,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_prospectos = repositorio_prospectos
        self.authorization_service = authorization_service

    def ejecutar(self, id: int, porcentaje_depreciacion_personalizado: float | None, usuario: Usuario):
        prospecto = self.repositorio_prospectos.buscar_prospecto_condominio(id)

        if prospecto is None:
            raise RecursoNoEncontradoException('Prospecto no encontrado')

        if not self.authorization_service.usuario_puede_establecer_depreciacion_personalizada(prospecto, usuario):
            raise UsuarioNoAutorizadoException

        prospecto.porcentaje_depreciacion_personalizado = porcentaje_depreciacion_personalizado
        self.repositorio_prospectos.actualizar_prospecto_condominio(prospecto)
