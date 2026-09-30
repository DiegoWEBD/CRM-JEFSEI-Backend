"""Servicio de auditoría: la única puerta de entrada de eventos (§14).

El endpoint sólo entrega lo específico del evento; usuario, IP, request id,
sesión, User-Agent y endpoint salen del AuditContext que armó el middleware.
"""

import logging
from typing import Any, Optional

from psycopg import Connection
from psycopg.rows import DictRow

from app.core.config import settings
from app.dominio.auditoria.auditoria_evento import AuditoriaEvento
from app.dominio.auditoria.enums import (
    Categoria,
    EVENTOS_CRITICOS,
    Resultado,
    TipoEvento,
)
from app.dominio.auditoria.repositorio_auditoria import RepositorioAuditoria
from app.infraestructura.auditoria.calculadora_cambios import calculate_changes
from app.infraestructura.auditoria.contexto_auditoria import AuditContext
from app.infraestructura.auditoria.middleware_auditoria import (
    CLAVE_ESTADO,
    normalizar_request_id,
)
from app.infraestructura.auditoria.redactador import preparar_json

logger = logging.getLogger(__name__)

# Cuando no hay contexto de request (login, tareas del scheduler, uso desde
# tests) se genera un request id propio para que el registro no quede huérfano.
SIN_CONTEXTO = AuditContext(request_id=normalizar_request_id(None))


class FallaAuditoriaCritica(Exception):
    """La auditoría de un evento crítico no se pudo escribir (fail-closed, §22)."""


class AuditService:

    def __init__(self, repositorio: RepositorioAuditoria) -> None:
        self.repositorio = repositorio

    def contexto_de(self, scope: dict | None) -> AuditContext:
        if not scope:
            return SIN_CONTEXTO
        contexto = scope.get(CLAVE_ESTADO)
        return contexto if isinstance(contexto, AuditContext) else SIN_CONTEXTO

    def con_usuario(
        self,
        scope: dict | None,
        rut_usuario: str | None,
        id_sesion: str | None = None,
    ) -> dict | None:
        """Agrega identidad al contexto de la request y lo devuelve.

        El middleware arma el contexto antes de saber quién se autentica, así
        que login y refresh necesitan completarlo. Se reasigna en el scope
        porque ``AuditContext`` es inmutable por diseño: el resto de la request
        ve la versión enrichcida.
        """
        if not scope:
            return scope
        contexto = scope.get(CLAVE_ESTADO)
        if not isinstance(contexto, AuditContext):
            return scope
        scope[CLAVE_ESTADO] = contexto.con(
            rut_usuario=rut_usuario,
            id_sesion=id_sesion,
        )
        return scope

    def log(
        self,
        event_type: TipoEvento,
        category: Categoria,
        result: Resultado,
        scope: dict | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        description: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        changes: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        error_code: str | None = None,
        status_http: int | None = None,
        conn: Optional[Connection[DictRow]] = None,
    ) -> AuditoriaEvento:
        if not settings.AUDIT_ENABLED:
            return self._evento_vacio()

        contexto = self.contexto_de(scope)

        # El diff se calcula acá si el endpoint no lo pasó: así el servicio
        # garantiza que un UPDATE siempre queda con "cambios" (§35).
        if changes is None and (before is not None or after is not None):
            changes = calculate_changes(before, after)

        metadata_completa = dict(contexto.metadata or {})
        if metadata:
            metadata_completa.update(metadata)

        evento = AuditoriaEvento(
            id=None,
            fecha_hora=None,
            rut_usuario=contexto.rut_usuario,
            tipo_evento=event_type,
            categoria=category,
            resultado=result,
            request_id=contexto.request_id,
            metodo_http=contexto.metodo_http,
            endpoint=contexto.endpoint,
            path=contexto.path,
            ip_origen=contexto.ip_origen,
            user_agent=contexto.user_agent,
            origin=contexto.origin,
            referer=contexto.referer,
            id_sesion=contexto.id_sesion,
            recurso_tipo=resource_type,
            recurso_id=resource_id,
            descripcion=description,
            datos_antes=_a_json(before),
            datos_despues=_a_json(after),
            cambios=_a_json(changes),
            metadata=_a_json(metadata_completa) if metadata_completa else None,
            duracion_ms=contexto.duracion_ms,
            status_http=status_http if status_http is not None else contexto.status_http,
            error_codigo=error_code,
            created_at=None,
        )

        return self._escribir(evento, conn)

    def _escribir(
        self,
        evento: AuditoriaEvento,
        conn: Optional[Connection[DictRow]],
    ) -> AuditoriaEvento:
        try:
            return self.repositorio.registrar(evento, conn=conn)

        except Exception as error:
            # Nunca se traga el error en silencio (§22).
            logger.error(
                'AUDIT_WRITE_FAILED request_id=%s event_type=%s error=%s',
                evento.request_id,
                evento.tipo_evento,
                error,
                extra={
                    'request_id': evento.request_id,
                    'event_type': str(evento.tipo_evento),
                },
                exc_info=True,
            )
            if evento.tipo_evento in EVENTOS_CRITICOS:
                raise FallaAuditoriaCritica(
                    f'No se pudo auditar {evento.tipo_evento}: {error}'
                ) from error
            return evento

    @staticmethod
    def _evento_vacio() -> AuditoriaEvento:
        return AuditoriaEvento(
            id=None, fecha_hora=None, rut_usuario=None,
            tipo_evento=TipoEvento.SYSTEM, categoria=Categoria.SYSTEM,
            resultado=Resultado.SUCCESS, request_id=normalizar_request_id(None),
        )


def _a_json(valor: Any) -> dict | None:
    return preparar_json(valor)
