from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)
from app.dominio.administrador_condominio.repositorio_administradores import (
    RepositorioAdministradores,
)
from app.dominio.exceptions.recurso_no_encontrado import (
    RecursoNoEncontradoException,
)


class ActualizarAdministradorUseCase:

    def __init__(self, repositorio_administradores: RepositorioAdministradores):
        self.repositorio_administradores = repositorio_administradores

    def ejecutar(
        self,
        id: int,
        nombre_administrador: str,
        nombre_contacto: str | None,
        telefono: str | None,
        correo: str | None,
    ) -> AdministradorCondominio:
        existente = self.repositorio_administradores.buscar(id)
        if not existente:
            raise RecursoNoEncontradoException(
                "Administrador no encontrado"
            )

        administrador = AdministradorCondominio(
            id=id,
            nombre_administrador=nombre_administrador,
            nombre_contacto=nombre_contacto,
            telefono=telefono,
            correo=correo,
        )

        return self.repositorio_administradores.actualizar(administrador)
