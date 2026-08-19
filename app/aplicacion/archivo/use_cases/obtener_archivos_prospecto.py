from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.archivo.archivo import Archivo
from app.dominio.archivo.repositorio_archivos import RepositorioArchivos
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class ObtenerArchivosProspectoUseCase:

    def __init__(
        self,
        repositorio_archivos: RepositorioArchivos,
        repositorio_prospectos: RepositorioProspectos,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_archivos = repositorio_archivos
        self.repositorio_prospectos = repositorio_prospectos
        self.authorization_service = authorization_service

    def ejecutar(self, id_prospecto: int, rut_usuario: str) -> list[Archivo]:
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if prospecto is None:
            raise RecursoNoEncontradoException("No se encontró el prospecto")

        if not self.authorization_service.usuario_puede_ver_prospecto(rut_usuario, id_prospecto):
            raise UsuarioNoAutorizadoException

        return self.repositorio_archivos.listar_por_prospecto(id_prospecto)
