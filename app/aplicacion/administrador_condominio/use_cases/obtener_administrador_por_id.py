from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)
from app.dominio.administrador_condominio.repositorio_administradores import (
    RepositorioAdministradores,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario


class ObtenerAdministradorPorIdUseCase:

    def __init__(
        self,
        repositorio_administradores: RepositorioAdministradores,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_administradores = repositorio_administradores
        self.authorization_service = authorization_service

    def ejecutar(self, usuario: Usuario, id: int) -> AdministradorCondominio:
        if not self.authorization_service.usuario_puede_ver_administradores(usuario):
            raise UsuarioNoAutorizadoException(
                "No tiene permiso para ver administradores de condominio"
            )

        administrador = self.repositorio_administradores.buscar(id)

        if administrador is None or administrador.id is None:
            raise RecursoNoEncontradoException(
                "No se encontró el administrador"
            )

        return administrador
