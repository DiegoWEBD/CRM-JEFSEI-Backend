from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.contacto.repositorio_contactos import RepositorioContactos
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException


class EliminarContactoUseCase:

    def __init__(
        self,
        repositorio_contactos: RepositorioContactos,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_contactos = repositorio_contactos
        self.authorization_service = authorization_service

    def ejecutar(self, id: int, rut_usuario: str) -> bool:
        existente = self.repositorio_contactos.buscar(id)

        if existente is None:
            raise RecursoNoEncontradoException("No se encontró el contacto")

        if not self.authorization_service.usuario_puede_ver_prospecto(rut_usuario, existente.id_prospecto):
            raise UsuarioNoAutorizadoException

        return self.repositorio_contactos.eliminar(id)