from app.aplicacion.permiso.use_cases.obtener_permisos import ObtenerPermisosUseCase
from app.infraestructura.permiso.repositorio_permisos_postgres import RepositorioPermisosPostgres


def get_obtener_permisos_use_case():
    repositorio_permisos = RepositorioPermisosPostgres()

    return ObtenerPermisosUseCase(
        repositorio_permisos=repositorio_permisos
    )
