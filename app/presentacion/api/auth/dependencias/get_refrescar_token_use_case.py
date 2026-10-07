from app.aplicacion.auth.use_cases.refrescar_token import RefrescarTokenUseCase
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.auth.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


def get_refrescar_token_use_case():
    repositorio = RepositorioUsuariosPostgres()
    authentication_service = JwtAuthenticationService(RepositorioSesionesPostgres())
    yield RefrescarTokenUseCase(repositorio, authentication_service)
