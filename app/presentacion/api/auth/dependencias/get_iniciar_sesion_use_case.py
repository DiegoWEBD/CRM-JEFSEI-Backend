from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


def get_iniciar_sesion_use_case():
    repositorio = RepositorioUsuariosPostgres()
    authentication_service = JwtAuthenticationService()
    yield IniciarSesionUseCase(repositorio, authentication_service)