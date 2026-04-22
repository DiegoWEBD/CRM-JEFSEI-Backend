from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.aplicacion.usuario.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


def get_obtener_usuario_use_case():
    repositorio = RepositorioUsuariosPostgres()
    return ObtenerUsuarioUseCase(repositorio)

def get_registrar_usuario_use_case():
    repositorio = RepositorioUsuariosPostgres()
    authentication_service = JwtAuthenticationService()
    return RegistrarUsuarioUseCase(repositorio, authentication_service)