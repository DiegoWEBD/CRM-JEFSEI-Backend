from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)
from app.dominio.administrador_condominio.repositorio_administradores import (
    RepositorioAdministradores,
)


class RegistrarAdministradorUseCase:

    def __init__(self, repositorio_administradores: RepositorioAdministradores):
        self.repositorio_administradores = repositorio_administradores

    def ejecutar(
        self,
        nombre_administrador: str,
        nombre_contacto: str | None,
        telefono: str | None,
        correo: str | None,
    ) -> AdministradorCondominio:
        administrador = AdministradorCondominio(
            id=None,
            nombre_administrador=nombre_administrador,
            nombre_contacto=nombre_contacto,
            telefono=telefono,
            correo=correo,
        )

        return self.repositorio_administradores.guardar(administrador)
