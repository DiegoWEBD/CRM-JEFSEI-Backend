from app.dominio.auditoria.registro_auditoria import RegistroAuditoria
from app.presentacion.api.auditoria.dto.registro_auditoria_json import RegistroAuditoriaJson


def registro_auditoria_a_json(registro: RegistroAuditoria) -> RegistroAuditoriaJson:
    return RegistroAuditoriaJson(
        id=registro.id if registro.id is not None else 0,
        fecha_registro=registro.fecha_registro,
        categoria=registro.categoria,
        evento=registro.evento,
        resultado=registro.resultado,
        estado_http=registro.estado_http,
        rut_usuario=registro.rut_usuario,
        nombre_usuario=registro.nombre_usuario,
        ip_origen=registro.ip_origen,
        user_agent=registro.user_agent,
        id_peticion=registro.id_peticion,
        metodo=registro.metodo,
        ruta=registro.ruta,
        entidad_tipo=registro.entidad_tipo,
        entidad_id=registro.entidad_id,
        detalle=registro.detalle,
        duracion_ms=registro.duracion_ms,
    )
