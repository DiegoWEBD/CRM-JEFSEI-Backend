from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.dominio.auditoria.eventos_auditoria import EventoAuditoria, ResultadoAuditoria


class CerrarSesionUseCase:

    def __init__(self, servicio_auditoria: ServicioAuditoria) -> None:
        self.servicio_auditoria = servicio_auditoria

    def ejecutar(self, rut: str, nombre: str | None, contexto: ContextoPeticion) -> None:
        self.servicio_auditoria.registrar_autenticacion(
            evento=EventoAuditoria.LOGOUT,
            resultado=ResultadoAuditoria.EXITO,
            contexto=contexto,
            rut_usuario=rut,
            nombre_usuario=nombre,
        )
