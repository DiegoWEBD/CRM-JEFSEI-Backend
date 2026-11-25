from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)
from app.dominio.administrador_condominio.repositorio_administradores import (
    RepositorioAdministradores,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException


class ObtenerAdministradorPorIdUseCase:

    def __init__(self, repositorio_administradores: RepositorioAdministradores):
        self.repositorio_administradores = repositorio_administradores

    def ejecutar(self, id: int) -> AdministradorCondominio:
        administrador = self.repositorio_administradores.buscar(id)

        if administrador is None or administrador.id is None:
            raise RecursoNoEncontradoException(
                "No se encontró el administrador"
            )

        return administrador
