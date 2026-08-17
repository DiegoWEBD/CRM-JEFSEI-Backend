from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.contacto.contacto import Contacto
from app.dominio.contacto.repositorio_contactos import RepositorioContactos
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException


class ActualizarContactoUseCase:

    def __init__(
        self,
        repositorio_contactos: RepositorioContactos,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_contactos = repositorio_contactos
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        id: int,
        nombre: str,
        telefono: str | None,
        correo: str | None,
        cargo: str | None,
        rut_usuario: str,
    ) -> Contacto:
        existente = self.repositorio_contactos.buscar(id)

        if existente is None:
            raise RecursoNoEncontradoException("No se encontró el contacto")

        if not self.authorization_service.usuario_puede_ver_prospecto(rut_usuario, existente.id_prospecto):
            raise UsuarioNoAutorizadoException

        contacto = Contacto(
            id=id,
            id_prospecto=existente.id_prospecto,
            nombre=nombre,
            telefono=telefono,
            correo=correo,
            cargo=cargo,
        )

        return self.repositorio_contactos.actualizar(contacto)