from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.dominio.auth.repositorio_sesiones import RepositorioSesiones


class RevocarTodasSesionesUsuarioAdminUseCase:

    def __init__(
        self,
        repositorio: RepositorioSesiones,
        servicio_auditoria: ServicioAuditoria,
    ) -> None:
        self.repositorio = repositorio
        self.servicio_auditoria = servicio_auditoria

    def ejecutar(
        self,
        rut_usuario: str,
        admin_rut: str,
        admin_nombre: str | None,
        contexto: ContextoPeticion,
    ) -> None:
        self.repositorio.revocar_sesiones_usuario(
            rut_usuario, motivo='revocacion_admin'
        )

        self.servicio_auditoria.registrar_autenticacion(
            evento='REVOCAR_TODAS_SESIONES',
            resultado='EXITO',
            contexto=contexto,
            rut_usuario=admin_rut,
            nombre_usuario=admin_nombre,
            detalle=f'Todas las sesiones del usuario {rut_usuario} revocadas por administrador',
        )