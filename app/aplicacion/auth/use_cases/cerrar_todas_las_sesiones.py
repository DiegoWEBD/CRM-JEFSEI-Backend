from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.aplicacion.auth.authentication_service import AuthenticationService
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria


class CerrarTodasLasSesionesUseCase:

    def __init__(
        self,
        servicio_auditoria: ServicioAuditoria,
        authentication_service: AuthenticationService,
    ) -> None:
        self.servicio_auditoria = servicio_auditoria
        self.authentication_service = authentication_service

    def ejecutar(
        self,
        rut: str,
        nombre: str | None,
        contexto: ContextoPeticion,
    ) -> None:
        self.authentication_service.revocar_todas_las_sesiones(rut, motivo='logout_all')

        self.servicio_auditoria.registrar_autenticacion(
            evento='LOGOUT_ALL',
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            rut_usuario=rut,
            nombre_usuario=nombre,
        )
