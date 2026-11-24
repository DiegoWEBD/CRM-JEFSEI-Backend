from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)
from app.dominio.administrador_condominio.repositorio_administradores import (
    RepositorioAdministradores,
)
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario


class RegistrarAdministradorUseCase:

    def __init__(
        self,
        repositorio_administradores: RepositorioAdministradores,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_administradores = repositorio_administradores
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        usuario: Usuario,
        nombre_administrador: str,
        nombre_contacto: str | None,
        telefono: str | None,
        correo: str | None,
    ) -> AdministradorCondominio:
        if not self.authorization_service.usuario_puede_administrar_administradores(usuario):
            raise UsuarioNoAutorizadoException(
                "No tiene permiso para administrar administradores de condominio"
            )

        # Solo datos básicos: la relación de condominios bajo administración
        # se gestiona desde el módulo de prospectos, fuera de este permiso.
        administrador = AdministradorCondominio(
            id=None,
            nombre_administrador=nombre_administrador,
            nombre_contacto=nombre_contacto,
            telefono=telefono,
            correo=correo,
        )

        return self.repositorio_administradores.guardar(administrador)
