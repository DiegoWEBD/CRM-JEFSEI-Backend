from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.archivo.archivo import Archivo
from app.dominio.archivo.repositorio_archivos import RepositorioArchivos
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos


class SubirArchivoUseCase:

    def __init__(
        self,
        repositorio_archivos: RepositorioArchivos,
        repositorio_prospectos: RepositorioProspectos,
        authorization_service: AuthorizationService,
    ):
        self.repositorio_archivos = repositorio_archivos
        self.repositorio_prospectos = repositorio_prospectos
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        id_prospecto: int,
        nombre_almacenado: str,
        nombre_original: str,
        tipo_contenido: str,
        tamano_bytes: int,
        rut_usuario: str,
    ) -> Archivo:
        prospecto = self.repositorio_prospectos.buscar(id_prospecto)

        if prospecto is None:
            raise RecursoNoEncontradoException("No se encontró el prospecto")

        if not self.authorization_service.usuario_puede_ver_prospecto(rut_usuario, id_prospecto):
            raise UsuarioNoAutorizadoException

        if self.repositorio_archivos.existe_nombre_almacenado(id_prospecto, nombre_almacenado):
            raise RecursoYaExisteException("Ya existe un archivo con ese nombre para este prospecto")

        return self.repositorio_archivos.insertar(
            id_prospecto=id_prospecto,
            nombre_almacenado=nombre_almacenado,
            nombre_original=nombre_original,
            tipo_contenido=tipo_contenido,
            tamano_bytes=tamano_bytes,
            rut_subido_por=rut_usuario,
        )
