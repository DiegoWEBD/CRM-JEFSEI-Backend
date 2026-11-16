from app.dominio.permiso.permiso import Permiso
from app.dominio.permiso.repositorio_permisos import RepositorioPermisos


class ObtenerPermisosUseCase:

    def __init__(self, repositorio_permisos: RepositorioPermisos):
        self.repositorio_permisos = repositorio_permisos

    def ejecutar(self) -> list[Permiso]:
        return self.repositorio_permisos.obtener_todos()
