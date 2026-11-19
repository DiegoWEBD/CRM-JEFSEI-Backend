from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.recordatorio.recordatorio_usuario.recordatorio_usuario import RecordatorioUsuario
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from app.dominio.usuario.usuario import Usuario


class ObtenerProximoContactoUseCase:

    def __init__(
        self,
        repositorio_recordatorio: RepositorioRecordatorios,
        authorization_service: AuthorizationService
    ) -> None:
        self.repositorio_recordatorio = repositorio_recordatorio
        self.authorization_service = authorization_service

    def ejecutar(self, usuario: Usuario, rut_objetivo: str, id_prospecto: int) -> RecordatorioUsuario | None:
        if rut_objetivo != usuario.rut:
            if not self.authorization_service.usuario_puede_gestionar_recordatorio_ajeno(usuario):
                raise UsuarioNoAutorizadoException(
                    'No tiene permiso para ver el próximo contacto de otro usuario'
                )

        return self.repositorio_recordatorio.obtener_proximo_contacto(rut_objetivo, id_prospecto)
