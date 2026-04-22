from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


def get_obtener_usuario_use_case():
    repositorio = RepositorioUsuariosPostgres()
    return ObtenerUsuarioUseCase(repositorio)