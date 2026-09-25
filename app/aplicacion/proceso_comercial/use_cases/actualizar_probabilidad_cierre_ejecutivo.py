from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.usuario.usuario import Usuario


class ActualizarProbabilidadCierreEjecutivoUseCase:

    def __init__(
        self,
        authorization_service: AuthorizationService,
        repositorio_procesos_comerciales: RepositorioProcesosComerciales,
    ):
        self.authorization_service = authorization_service
        self.repositorio_procesos_comerciales = repositorio_procesos_comerciales

    def ejecutar(self, id: int, probabilidad_cierre_ejecutivo: float | None, usuario: Usuario):
        proceso = self.repositorio_procesos_comerciales.buscar(id)

        if not proceso:
            raise RecursoNoEncontradoException(f'No se encontró la oportunidad comercial {id}')

        if not self.authorization_service.usuario_puede_actualizar_probabilidad_cierre(
            rut_usuario=usuario.rut,
            id_proceso_comercial=id,
        ):
            raise UsuarioNoAutorizadoException('No autorizado para actualizar la probabilidad de cierre')

        if proceso.cerrado:
            raise ConflictoEnAccionException('La oportunidad está cerrada')

        self.repositorio_procesos_comerciales.actualizar_probabilidad_cierre_ejecutivo(
            id=id,
            probabilidad=probabilidad_cierre_ejecutivo,
        )
