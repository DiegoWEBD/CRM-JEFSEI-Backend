from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerProspectoLineasPersonalesUseCase:
    def __init__(
        self, 
        authorization_service: AuthorizationService,
        repositorio_prospectos: RepositorioProspectos,
    ):
        self.authorization_service = authorization_service
        self.repositorio_prospectos = repositorio_prospectos

    def ejecutar(self, id: int, rut_usuario: str | None) -> Prospecto:
        prospecto = self.repositorio_prospectos.buscar(id)

        if prospecto is None or prospecto.id is None:
            raise RecursoNoEncontradoException('No se encontró el prospecto')

        if rut_usuario and not self.authorization_service.usuario_puede_ver_prospecto(rut_usuario, prospecto.id):
            raise UsuarioNoAutorizadoException

        return prospecto
    