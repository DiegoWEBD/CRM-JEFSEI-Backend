from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from app.dominio.usuario.usuario import Usuario


class ActualizarRecordatorioUseCase:

    def __init__(
        self,
        repositorio_recordatorios: RepositorioRecordatorios,
        authorization_service: AuthorizationService
    ):
        self.repositorio_recordatorios = repositorio_recordatorios
        self.authorization_service = authorization_service

    def ejecutar(
        self,
        usuario: Usuario,
        id: int,
        titulo: str,
        detalle: str | None,
        prioridad: str,
        tipo_gestion: str,
        fecha_recordatorio: str,
        id_prospecto: int | None = None,
    ) -> None:
        propietarios = self.repositorio_recordatorios.buscar_propietarios(id)

        if propietarios is None:
            raise RecursoNoEncontradoException('El recordatorio no existe')

        if not self.authorization_service.usuario_puede_gestionar_recordatorio(usuario, id):
            raise UsuarioNoAutorizadoException('No tiene permiso para actualizar este recordatorio')

        self.repositorio_recordatorios.actualizar(
            id=id,
            titulo=titulo,
            detalle=detalle,
            prioridad=prioridad,
            tipo_gestion=tipo_gestion,
            fecha_recordatorio=fecha_recordatorio,
            id_prospecto=id_prospecto,
        )
