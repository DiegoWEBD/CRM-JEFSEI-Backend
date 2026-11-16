from app.aplicacion.rol.use_cases.asignar_permisos_rol import AsignarPermisosRolUseCase
from app.aplicacion.rol.use_cases.obtener_roles import ObtenerRolesUseCase
from app.aplicacion.rol.use_cases.obtener_roles_con_permisos import ObtenerRolesConPermisosUseCase
from app.infraestructura.permiso.repositorio_permisos_postgres import RepositorioPermisosPostgres
from app.infraestructura.rol.repositorio_roles_postgres import RepositorioRolesPostgres
from app.presentacion.api.auditoria.dependencias.deps import get_servicio_auditoria


def get_obtener_roles_use_case():
    repositorio_roles = RepositorioRolesPostgres()

    return ObtenerRolesUseCase(
        repositorio_roles=repositorio_roles
    )


def get_obtener_roles_con_permisos_use_case():
    repositorio_roles = RepositorioRolesPostgres()

    return ObtenerRolesConPermisosUseCase(
        repositorio_roles=repositorio_roles
    )


def get_asignar_permisos_rol_use_case():
    repositorio_roles = RepositorioRolesPostgres()
    repositorio_permisos = RepositorioPermisosPostgres()
    servicio_auditoria = get_servicio_auditoria()

    return AsignarPermisosRolUseCase(
        repositorio_roles=repositorio_roles,
        repositorio_permisos=repositorio_permisos,
        servicio_auditoria=servicio_auditoria
    )
