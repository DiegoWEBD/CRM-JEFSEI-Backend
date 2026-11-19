from app.aplicacion.authorization.authorization_service_factory import AuthorizationServiceFactory
from app.aplicacion.usuario.use_cases.actualizar_perfil import ActualizarPerfilUseCase
from app.aplicacion.usuario.use_cases.actualizar_roles_usuario import ActualizarRolesUsuarioUseCase
from app.aplicacion.usuario.use_cases.actualizar_usuario import ActualizarUsuarioUseCase
from app.aplicacion.usuario.use_cases.cambiar_password import CambiarPasswordUseCase
from app.aplicacion.usuario.use_cases.eliminar_usuario import EliminarUsuarioUseCase
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.aplicacion.usuario.use_cases.obtener_usuarios import ObtenerUsuariosUseCase
from app.aplicacion.usuario.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.infraestructura.auth.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.infraestructura.rol.repositorio_roles_postgres import RepositorioRolesPostgres
from app.infraestructura.usuario.repositorio_usuarios_postgres import RepositorioUsuariosPostgres
from app.presentacion.api.auditoria.dependencias.deps import get_servicio_auditoria


def get_obtener_usuario_use_case():
    return ObtenerUsuarioUseCase(
        repositorio_usuarios=RepositorioUsuariosPostgres(),
        authorization_service=AuthorizationServiceFactory.crear_authorization_service()
    )

def get_obtener_usuarios_use_case():
    repositorio = RepositorioUsuariosPostgres()
    return ObtenerUsuariosUseCase(repositorio)

def get_registrar_usuario_use_case():
    repositorio = RepositorioUsuariosPostgres()
    authentication_service = JwtAuthenticationService(RepositorioSesionesPostgres())
    return RegistrarUsuarioUseCase(repositorio, authentication_service)

def get_actualizar_usuario_use_case():
    repositorio = RepositorioUsuariosPostgres()
    authentication_service = JwtAuthenticationService(RepositorioSesionesPostgres())
    return ActualizarUsuarioUseCase(repositorio, authentication_service)

def get_actualizar_perfil_use_case():
    repositorio = RepositorioUsuariosPostgres()
    servicio_auditoria = get_servicio_auditoria()
    return ActualizarPerfilUseCase(repositorio, servicio_auditoria)

def get_cambiar_password_use_case():
    repositorio = RepositorioUsuariosPostgres()
    authentication_service = JwtAuthenticationService(RepositorioSesionesPostgres())
    servicio_auditoria = get_servicio_auditoria()
    return CambiarPasswordUseCase(repositorio, authentication_service, servicio_auditoria)

def get_actualizar_roles_usuario_use_case():
    repositorio = RepositorioUsuariosPostgres()
    repositorio_roles = RepositorioRolesPostgres()
    servicio_auditoria = get_servicio_auditoria()
    return ActualizarRolesUsuarioUseCase(repositorio, repositorio_roles, servicio_auditoria)

def get_eliminar_usuario_use_case():
    repositorio = RepositorioUsuariosPostgres()
    return EliminarUsuarioUseCase(repositorio)