from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.dominio.usuario.usuario import Usuario


class ObtenerUsuarioUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, rut: str) -> Usuario:
        usuario = self.repositorio_usuarios.buscar(rut)

        if usuario is None:
            raise RecursoNoEncontradoException("Usuario no encontrado")
        
        return usuario