from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.dominio.auditoria.eventos_auditoria import (
    CategoriaAuditoria,
    EventoAuditoria,
    ResultadoAuditoria,
)
from app.dominio.auditoria.registro_auditoria import RegistroAuditoria


def crear_contexto_peticion_mock(
    ip_origen: str = "200.10.20.30",
    user_agent: str | None = "Mozilla/5.0",
    id_peticion: str | None = "id-peticion-test",
) -> ContextoPeticion:
    return ContextoPeticion(
        ip_origen=ip_origen,
        user_agent=user_agent,
        id_peticion=id_peticion,
    )


def crear_registro_auditoria_mock(**kwargs) -> RegistroAuditoria:
    defaults = dict(
        categoria=CategoriaAuditoria.ACCION_NEGOCIO,
        evento=EventoAuditoria.CREAR,
        resultado=ResultadoAuditoria.EXITO,
        estado_http=201,
        rut_usuario="12345678-9",
        nombre_usuario="Juan Perez",
        ip_origen="200.10.20.30",
        user_agent="Mozilla/5.0",
        id_peticion="id-peticion-test",
        metodo="POST",
        ruta="/prospectos/",
        entidad_tipo="prospectos",
        entidad_id=None,
        detalle=None,
        duracion_ms=12,
    )
    defaults.update(kwargs)
    return RegistroAuditoria(**defaults)


def crear_fila_registro_auditoria_mock(**kwargs) -> dict:
    defaults = dict(
        id=1,
        fecha_registro="2026-09-30T12:00:00+00:00",
        categoria=CategoriaAuditoria.ACCION_NEGOCIO,
        evento=EventoAuditoria.CREAR,
        resultado=ResultadoAuditoria.EXITO,
        estado_http=201,
        rut_usuario="12345678-9",
        nombre_usuario="Juan Perez",
        ip_origen="200.10.20.30",
        user_agent="Mozilla/5.0",
        id_peticion="id-peticion-test",
        metodo="POST",
        ruta="/prospectos/",
        entidad_tipo="prospectos",
        entidad_id=None,
        detalle=None,
        duracion_ms=12,
    )
    defaults.update(kwargs)
    return defaults
