from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class ObtenerUsuarioUseCase:
    def __init__(
        self, 
        repositorio_usuarios: RepositorioUsuarios,
        authorization_service: AuthorizationService
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.authorization_service = authorization_service

    def ejecutar(self, rut_consultado: str, usuario_accion: Usuario) -> Usuario:

        if not self.authorization_service.usuario_puede_ver_perfil(usuario_accion, rut_consultado):
            raise UsuarioNoAutorizadoException

        usuario = self.repositorio_usuarios.buscar(rut_consultado)

        if usuario is None:
            raise RecursoNoEncontradoException("Usuario no encontrado")
        
        return usuario