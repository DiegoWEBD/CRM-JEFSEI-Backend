from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.contacto.contacto import Contacto
from app.dominio.contacto.repositorio_contactos import RepositorioContactos
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerContactosProspectoUseCase:

    def __init__(
        self,
        repositorio_contactos: RepositorioContactos,
        repositorio_prospectos: RepositorioProspectos,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_contactos = repositorio_contactos
        self.repositorio_prospectos = repositorio_prospectos
        self.authorization_service = authorization_service

    def ejecutar(self, id_prospecto: int, rut_usuario: str) -> list[Contacto]:
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if prospecto is None:
            raise RecursoNoEncontradoException("No se encontró el prospecto")

        if not self.authorization_service.usuario_puede_ver_prospecto(rut_usuario, id_prospecto):
            raise UsuarioNoAutorizadoException

        return self.repositorio_contactos.obtener_por_prospecto(id_prospecto)