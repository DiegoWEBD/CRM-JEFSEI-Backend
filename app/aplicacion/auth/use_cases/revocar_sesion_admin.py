from uuid import UUID

from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.dominio.auth.repositorio_sesiones import RepositorioSesiones
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException


class RevocarSesionAdminUseCase:

    def __init__(
        self,
        repositorio: RepositorioSesiones,
        servicio_auditoria: ServicioAuditoria,
    ) -> None:
        self.repositorio = repositorio
        self.servicio_auditoria = servicio_auditoria

    def ejecutar(
        self,
        sesion_id: UUID,
        admin_rut: str,
        admin_nombre: str | None,
        contexto: ContextoPeticion,
    ) -> None:
        sesion = self.repositorio.obtener_sesion_viva(sesion_id)
        if sesion is None:
            raise RecursoNoEncontradoException(
                f'La sesión {sesion_id} no existe o ya fue revocada'
            )

        self.repositorio.revocar_sesion(sesion_id, motivo='revocacion_admin')

        self.servicio_auditoria.registrar_autenticacion(
            evento='REVOCAR_SESION',
            resultado='EXITO',
            contexto=contexto,
            rut_usuario=admin_rut,
            nombre_usuario=admin_nombre,
            detalle=f'Sesión {sesion_id} del usuario {sesion.rut_usuario} revocada por administrador',
        )