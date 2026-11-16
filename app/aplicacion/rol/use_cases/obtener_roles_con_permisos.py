from app.dominio.rol.repositorio_roles import RepositorioRoles
from app.dominio.rol.rol import Rol


class ObtenerRolesConPermisosUseCase:

    def __init__(self, repositorio_roles: RepositorioRoles):
        self.repositorio_roles = repositorio_roles

    def ejecutar(self) -> list[Rol]:
        return self.repositorio_roles.obtener_con_permisos()
