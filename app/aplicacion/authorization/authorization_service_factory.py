from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres
from app.infraestructura.prospecto.repositorio_prospectos_postgres import RepositorioProspectosPostgres
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres


class AuthorizationServiceFactory:

    @staticmethod
    def crear_authorization_service() -> AuthorizationService:
        return AuthorizationService(
            authorization_repository=AuthorizationRepositoryPostgres(),
            repositorio_usuarios=RepositorioUsuariosPostgres(),
            repositorio_prospectos=RepositorioProspectosPostgres()
        )