from psycopg import Connection
from psycopg.rows import DictRow

from app.aplicacion.auditoria.audit_service import AuditService
from app.dominio.auditoria.enums import Categoria, Resultado, TipoEvento
from app.dominio.auditoria.repositorio_sesiones import RepositorioSesiones


class CerrarSesionUseCase:
    """Cierre de sesión.

    Idempotente a propósito: un logout sobre una sesión ya cerrada es un
    resultado correcto, no un error. El frontend limpia cookies en ambos casos,
    así que fallar obligaría a distinguir estados que no le importan.
    """

    def __init__(
        self,
        repositorio_sesiones: RepositorioSesiones,
        audit_service: AuditService | None = None,
    ) -> None:
        self.repositorio_sesiones = repositorio_sesiones
        self.audit_service = audit_service

    def execute(
        self,
        id_sesion: str | None,
        scope: dict | None = None,
        conn: Connection[DictRow] | None = None,
    ) -> None:
        if not id_sesion:
            return

        sesion = self.repositorio_sesiones.obtener_por_id(id_sesion, conn=conn)
        if sesion is None:
            return

        if not sesion.esta_revocada():
            self.repositorio_sesiones.revocar(id_sesion, 'LOGOUT', conn=conn)
            self.repositorio_sesiones.revocar_refresh_tokens_de_sesion(id_sesion, conn=conn)

        if not self.audit_service:
            return

        scope = self.audit_service.con_usuario(scope, sesion.rut_usuario, sesion.id)
        self.audit_service.log(
            event_type=TipoEvento.LOGOUT,
            category=Categoria.AUTHENTICATION,
            result=Resultado.SUCCESS,
            scope=scope,
            description='Cierre de sesión',
            resource_type='Sesion',
            resource_id=sesion.id,
            conn=conn,
        )
