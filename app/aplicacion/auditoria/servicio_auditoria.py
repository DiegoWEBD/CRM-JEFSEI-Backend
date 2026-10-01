import logging

from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.dominio.auditoria.eventos_auditoria import CategoriaAuditoria, ResultadoAuditoria
from app.dominio.auditoria.registro_auditoria import RegistroAuditoria
from app.dominio.auditoria.repositorio_auditoria import RepositorioAuditoria

logger = logging.getLogger('auditoria')


class ServicioAuditoria:
    """Construye y persiste eventos de auditoría.

    La escritura es best-effort: un fallo de auditoría se registra en el log
    de aplicación pero nunca interrumpe la operación del usuario.
    """

    def __init__(self, repositorio_auditoria: RepositorioAuditoria) -> None:
        self.repositorio_auditoria = repositorio_auditoria

    def registrar_autenticacion(
        self,
        evento: str,
        resultado: str,
        contexto: ContextoPeticion,
        rut_usuario: str | None = None,
        nombre_usuario: str | None = None,
        detalle: str | None = None,
    ) -> None:
        registro = RegistroAuditoria(
            categoria=CategoriaAuditoria.AUTENTICACION,
            evento=evento,
            resultado=resultado,
            rut_usuario=rut_usuario,
            nombre_usuario=nombre_usuario,
            ip_origen=contexto.ip_origen,
            user_agent=contexto.user_agent,
            id_peticion=contexto.id_peticion,
            detalle=detalle,
        )
        self._registrar(registro)

    def registrar_accion_negocio(
        self,
        evento: str,
        resultado: str,
        contexto: ContextoPeticion,
        estado_http: int | None = None,
        rut_usuario: str | None = None,
        nombre_usuario: str | None = None,
        metodo: str | None = None,
        ruta: str | None = None,
        entidad_tipo: str | None = None,
        entidad_id: str | None = None,
        duracion_ms: int | None = None,
        detalle: str | None = None,
    ) -> None:
        registro = RegistroAuditoria(
            categoria=CategoriaAuditoria.ACCION_NEGOCIO,
            evento=evento,
            resultado=resultado,
            estado_http=estado_http,
            rut_usuario=rut_usuario,
            nombre_usuario=nombre_usuario,
            ip_origen=contexto.ip_origen,
            user_agent=contexto.user_agent,
            id_peticion=contexto.id_peticion,
            metodo=metodo,
            ruta=ruta,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            detalle=detalle,
            duracion_ms=duracion_ms,
        )
        self._registrar(registro)

    def _registrar(self, registro: RegistroAuditoria) -> None:
        try:
            self.repositorio_auditoria.registrar(registro)
        except Exception:
            logger.exception(
                'No se pudo registrar el evento de auditoría %s/%s',
                registro.categoria,
                registro.evento,
            )
