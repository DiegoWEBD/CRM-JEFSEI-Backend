from app.dominio.usuario.usuario import Usuario
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios

class RepositorioUsuariosImpl(RepositorioUsuarios):

    def buscar(self, rut: str) -> Usuario | None:
        return None

    def registrar(self, usuario: Usuario) -> bool:
        return False