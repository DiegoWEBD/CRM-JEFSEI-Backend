from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.auth.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres
from app.presentacion.api.auditoria.dependencias.deps import get_servicio_auditoria


def get_iniciar_sesion_use_case():
    repositorio = RepositorioUsuariosPostgres()
    authentication_service = JwtAuthenticationService(RepositorioSesionesPostgres())
    yield IniciarSesionUseCase(repositorio, authentication_service, get_servicio_auditoria())
