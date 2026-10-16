from app.aplicacion.archivo.servicios.servicio_archivos import ServicioArchivos
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.core.archivos import DIRECTORIO_PROSPECTOS
from app.dominio.archivo.repositorio_archivos import RepositorioArchivos
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class EliminarArchivoUseCase:

    def __init__(
        self,
        repositorio_archivos: RepositorioArchivos,
        repositorio_prospectos: RepositorioProspectos,
        authorization_service: AuthorizationService,
        servicio_archivos: ServicioArchivos,
    ):
        self.repositorio_archivos = repositorio_archivos
        self.repositorio_prospectos = repositorio_prospectos
        self.authorization_service = authorization_service
        self.servicio_archivos = servicio_archivos

    def ejecutar(self, id_archivo: int, id_prospecto: int, rut_usuario: str) -> None:
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if prospecto is None:
            raise RecursoNoEncontradoException("No se encontró el prospecto")

        if not self.authorization_service.usuario_puede_ver_prospecto(rut_usuario, id_prospecto):
            raise UsuarioNoAutorizadoException

        archivo = self.repositorio_archivos.obtener_por_id(id_archivo)

        if archivo is None:
            raise RecursoNoEncontradoException("No se encontró el archivo")

        if archivo.id_prospecto != id_prospecto:
            raise RecursoNoEncontradoException("El archivo no pertenece a este prospecto")

        self.repositorio_archivos.eliminar(id_archivo)

        self.servicio_archivos.eliminar(DIRECTORIO_PROSPECTOS, archivo.nombre_almacenado)