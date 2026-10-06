from app.aplicacion.auth.authentication_service import AuthenticationService
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.auth.repositorio_sesiones_postgres import RepositorioSesionesPostgres


def get_authentication_service_dependency() -> AuthenticationService:
    return JwtAuthenticationService(RepositorioSesionesPostgres())
