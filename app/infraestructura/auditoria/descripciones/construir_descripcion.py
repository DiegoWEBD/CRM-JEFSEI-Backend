import logging

from app.dominio.auditoria.eventos_auditoria import EventoAuditoria
from app.infraestructura.auditoria.descripciones.formatear import formatear_accion
from app.infraestructura.auditoria.descripciones.registro import REGISTRO
from app.infraestructura.auditoria.descripciones.resolvedor_nombres import ResolvedorNombres

logger = logging.getLogger('auditoria')

VERBO_GENERICO = {
    EventoAuditoria.CREAR: 'ha creado un registro en',
    EventoAuditoria.ACTUALIZAR: 'ha actualizado',
    EventoAuditoria.ELIMINAR: 'ha eliminado',
    EventoAuditoria.EJECUTAR_ACCION: 'ha ejecutado',
}


def descripcion_generica(evento: str, metodo: str, ruta: str, actor: str) -> str:
    segmentos = [segmento for segmento in ruta.split('/') if segmento]
    verbo = VERBO_GENERICO.get(evento, 'ha ejecutado')

    if evento == EventoAuditoria.CREAR and segmentos:
        return f'El usuario {actor} {verbo} {segmentos[0]}'

    if evento in (EventoAuditoria.ACTUALIZAR, EventoAuditoria.ELIMINAR) and len(segmentos) >= 2:
        return f'El usuario {actor} {verbo} {segmentos[0]} ({segmentos[1]})'

    return f'El usuario {actor} {verbo} {metodo} {ruta}'


def construir_descripcion_accion(
    metodo: str,
    ruta: str,
    evento_heuristico: str,
    actor: str | None,
    body: dict | None,
    resolvedor: ResolvedorNombres,
) -> tuple[str, str]:
    """Devuelve (evento_semantico, descripcion) para una petición mutante.

    El evento semántico lo declara el registro de descriptores (p. ej. crear
    una póliza sobre una oportunidad es CREAR aunque el POST sea a sub-ruta).
    Si la ruta no está registrada o el descriptor falla, se usa la frase y el
    evento genéricos.
    """
    actor = actor or 'desconocido'
    parametros = body if isinstance(body, dict) else {}

    for entrada in REGISTRO:
        if entrada.metodo != metodo:
            continue

        coincidencia = entrada.patron.match(ruta)
        if not coincidencia:
            continue

        try:
            accion = entrada.descriptor(coincidencia.groupdict(), parametros, resolvedor)
            return accion.evento, formatear_accion(actor, accion)
        except Exception:
            logger.exception('No se pudo construir la descripción para %s %s', metodo, ruta)
            break

    return evento_heuristico, descripcion_generica(evento_heuristico, metodo, ruta, actor)
