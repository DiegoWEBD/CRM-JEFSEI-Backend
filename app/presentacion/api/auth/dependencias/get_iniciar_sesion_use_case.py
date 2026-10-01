from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.infraestructura.auditoria.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres
from app.presentacion.api.auth.dependencias.get_sesion_use_cases import get_audit_service


def get_iniciar_sesion_use_case():
    yield IniciarSesionUseCase(
        RepositorioUsuariosPostgres(),
        JwtAuthenticationService(),
        repositorio_sesiones=RepositorioSesionesPostgres(),
        audit_service=get_audit_service(),
    )
