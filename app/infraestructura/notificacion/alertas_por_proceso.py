"""Operaciones sobre alertas (Notificacion) ligadas a un ProcesoComercial.

Ambas funciones trabajan sobre un cursor YA abierto, dentro de la transacción
del llamador (cambio de estado / reasignación de ejecutivo), de modo que los
cambios de alerta se confirman o revierten junto con el cambio de dominio.

No publican en el hub: la publicación es responsabilidad del método de
repositorio llamador, justo DESPUÉS de que la conexión haga commit.
"""

from datetime import datetime

from psycopg import Cursor, sql
from psycopg.rows import DictRow

# Roles responsables del estado actual del proceso -> destinatario de la alerta.
# El mismo mapa CAMPO_POR_ROL de GenerarAlertasSlaUseCase, en sentido inverso.
ROL_EJECUTIVO_COMERCIAL = 'EJECUTIVO_COMERCIAL'
ROL_EJECUTIVO_EVALUACION_PROYECTOS = 'EJECUTIVO_EVALUACION_PROYECTOS'

# Únicos tipos de alerta generados por permanencia en estado (SLA).
TIPOS_ALERTA_SLA = ('SLA_POR_VENCER', 'SLA_VENCIDO')

# Alertas basadas en fecha estimada de cierre: se marcan leídas al cerrar el
# proceso, NO en cada cambio de estado.
TIPOS_ALERTA_FECHA = ('CIERRE_ESTIMADO_PROXIMO', 'FECHA_CIERRE_VENCIDA')


def marcar_alertas_sla_leidas(
    cur: Cursor[DictRow],
    id_proceso: int,
    fecha: datetime,
) -> list[str]:
    """Marca como leídas las alertas SLA no leídas de un proceso comercial.

    Se usa al cambiar de estado: la alerta de permanencia en el estado anterior
    queda leída con la MISMA fecha del cambio. Devuelve los RUTs cuyas alertas
    fueron marcadas (para que el llamador publique el refresco correspondiente).
    """
    query = '''
        update Notificacion
        set leida = true,
        fecha_leida = %(fecha)s
        where entidad_tipo = 'PROCESO_COMERCIAL'
        and entidad_id = %(id_proceso)s
        and codigo_tipo = any(%(tipos_sla)s)
        and leida = false
        returning rut_usuario
    '''
    params = {
        'fecha': fecha,
        'id_proceso': id_proceso,
        'tipos_sla': list(TIPOS_ALERTA_SLA),
    }

    cur.execute(query, params)

    # rut_usuario puede ser NULL (alerta huérfana): no hay a quién notificar.
    return [
        row['rut_usuario'] for row in cur.fetchall() if row['rut_usuario']
    ]


def reasignar_destinatario_alertas(
    cur: Cursor[DictRow],
    id_prospecto: int,
    rol: str,
    nuevo_rut: str | None,
) -> tuple[set[str], set[str]]:
    """Cambia el destinatario de las alertas no leídas de los procesos abiertos
    de un prospecto cuyo estado siguiente (destino de la transición principal)
    tenga `rol` como responsable.

    - `nuevo_rut` con valor: las alertas pasan a ese ejecutivo.
    - `nuevo_rut` None (desasignación): las alertas quedan sin destinatario
      (rut_usuario = NULL) y serán reclamadas por el próximo asignado.

    Solo se tocan procesos NO cerrados y alertas cuyo destinatario actual
    difiera del nuevo. Devuelve (RUTs anteriores, RUTs nuevos).
    """
    condiciones: list[sql.Composable] = [
        sql.SQL("N.entidad_tipo = 'PROCESO_COMERCIAL'"),
        sql.SQL('N.leida = false'),
        sql.SQL('N.rut_usuario is distinct from %(nuevo_rut)s'),
        sql.SQL('PC.id_prospecto = %(id_prospecto)s'),
        sql.SQL('PC.cerrado = false'),
        sql.SQL('EI_SIGUIENTE.rol_responsable = %(rol)s'),
        sql.SQL("N.codigo_tipo != 'CIERRE_ESTIMADO_PROXIMO'"),
        sql.SQL("N.codigo_tipo != 'FECHA_CIERRE_VENCIDA'"),
    ]
    where_condiciones = sql.SQL(' AND ').join(condiciones)

    # Join con la transición principal + estado destino para resolver el
    # rol responsable del siguiente estado (no el actual).
    join_transicion = sql.SQL('''
        inner join TransicionEstadoProcesoComercial T
        on T.codigo_estado_origen = PC.codigo_estado_actual
        and T.es_principal = true
        inner join EstadoInformativoProcesoComercial EI_SIGUIENTE
        on EI_SIGUIENTE.codigo = T.codigo_estado_destino
    ''')

    params = {
        'id_prospecto': id_prospecto,
        'rol': rol,
        'nuevo_rut': nuevo_rut,
    }

    # 1) RUTs que recibirán el cambio (antes del update)
    query_previos = sql.SQL('''
        select distinct N.rut_usuario
        from Notificacion N
        inner join ProcesoComercial PC
        on PC.id = N.entidad_id
        {join_transicion}
        where {where_condiciones}
    ''').format(join_transicion=join_transicion, where_condiciones=where_condiciones)
    cur.execute(query_previos, params)
    # Puede traer NULL (alerta huérfana que será reclamada): sin destinatario
    # que notificar.
    previos = {
        row['rut_usuario'] for row in cur.fetchall() if row['rut_usuario']
    }

    # 2) Cambio de destinatario
    query_update = sql.SQL('''
        update Notificacion N
        set rut_usuario = %(nuevo_rut)s
        from ProcesoComercial PC
        {join_transicion}
        where N.entidad_id = PC.id
        and {where_condiciones}
    ''').format(join_transicion=join_transicion, where_condiciones=where_condiciones)
    cur.execute(query_update, params)

    if cur.rowcount == 0:
        return set(), set()

    nuevos = {nuevo_rut} if nuevo_rut else set()
    return previos, nuevos


def marcar_alertas_fecha_leidas(
    cur: Cursor[DictRow],
    id_proceso: int,
    fecha: datetime,
) -> list[str]:
    """Marca como leídas las alertas de fecha (cierre) no leídas de un proceso.

    Se usa al CERRAR el proceso: las alertas de cierre próximo / vencido dejan
    de ser relevantes. Devuelve los RUTs cuyas alertas fueron marcadas.
    """
    query = '''
        update Notificacion
        set leida = true,
        fecha_leida = %(fecha)s
        where entidad_tipo = 'PROCESO_COMERCIAL'
        and entidad_id = %(id_proceso)s
        and codigo_tipo = any(%(tipos_fecha)s)
        and leida = false
        returning rut_usuario
    '''
    params = {
        'fecha': fecha,
        'id_proceso': id_proceso,
        'tipos_fecha': list(TIPOS_ALERTA_FECHA),
    }

    cur.execute(query, params)

    return [
        row['rut_usuario'] for row in cur.fetchall() if row['rut_usuario']
    ]


def marcar_alertas_fecha_leidas_por_prospecto(
    cur: Cursor[DictRow],
    id_prospecto: int,
    fecha: datetime,
) -> list[str]:
    """Marca como leídas las alertas de fecha (cierre) no leídas del prospecto.

    Se usa al ASIGNAR/REASIGNAR/DESASIGNAR el ejecutivo comercial: las alertas
    de cierre próximo / vencido del ejecutivo anterior dejan de ser relevantes.
    Solo toca procesos NO cerrados. Devuelve los RUTs cuyas alertas fueron
    marcadas (para que el llamador publique el refresco correspondiente).
    """
    query = '''
        update Notificacion N
        set leida = true,
        fecha_leida = %(fecha)s
        from ProcesoComercial PC
        where PC.id = N.entidad_id
        and N.entidad_tipo = 'PROCESO_COMERCIAL'
        and PC.id_prospecto = %(id_prospecto)s
        and PC.cerrado = false
        and N.codigo_tipo = any(%(tipos_fecha)s)
        and N.leida = false
        returning N.rut_usuario
    '''
    params = {
        'fecha': fecha,
        'id_prospecto': id_prospecto,
        'tipos_fecha': list(TIPOS_ALERTA_FECHA),
    }

    cur.execute(query, params)

    return [
        row['rut_usuario'] for row in cur.fetchall() if row['rut_usuario']
    ]
