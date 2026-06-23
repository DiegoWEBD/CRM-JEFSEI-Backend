from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)
from app.dominio.administrador_condominio.repositorio_administradores import (
    RepositorioAdministradores,
)


class ObtenerAdministradoresUseCase:

    def __init__(self, repositorio_administradores: RepositorioAdministradores):
        self.repositorio_administradores = repositorio_administradores

    def ejecutar(self) -> list[AdministradorCondominio]:
        return self.repositorio_administradores.obtener_todos()
