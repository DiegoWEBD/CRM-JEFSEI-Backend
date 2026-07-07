from app.aplicacion.rol.use_cases.obtener_roles import ObtenerRolesUseCase
from app.infraestructura.rol.repositorio_roles_postgres import RepositorioRolesPostgres


def get_obtener_roles_use_case():
    repositorio_roles = RepositorioRolesPostgres()

    return ObtenerRolesUseCase(
        repositorio_roles=repositorio_roles
    )
