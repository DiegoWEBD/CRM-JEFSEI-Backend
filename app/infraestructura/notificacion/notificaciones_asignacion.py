"""Registro de notificaciones por asignación de ejecutivo/asistente.

Trabaja sobre un cursor YA abierto, dentro de la transacción del llamador
(asignación de ejecutivo), de modo que la notificación se confirma o revierte
junto con el cambio de dominio.

No publica en el hub: la publicación es responsabilidad del caso de uso.
"""

from datetime import datetime, timezone

from psycopg import Cursor
from psycopg.rows import DictRow

TIPO_ASIGNACION = 'ASIGNACION_EJECUTIVO'


def registrar_notificacion_asignacion(
    cur: Cursor[DictRow],
    *,
    rut_asignado: str,
    rol: str,
    entidad_tipo: str,
    entidad_id: int,
    nombre_entidad: str,
    id_prospecto: int | None = None,
) -> None:
    """Inserta una notificación de asignación dentro de la transacción del llamador.

    Solo debe llamarse cuando se asigna un ejecutivo (rut_asignado no es None).
    No retorna nada: el caso de uso conoce el destinatario y publica en el hub.
    """
    ahora = datetime.now(tz=timezone.utc)

    titulo = f'Asignación de {rol}'
    mensaje = f'Se le ha asignado como {rol} del {entidad_tipo.lower()} {nombre_entidad}.'

    query = '''
        insert into Notificacion(
            rut_usuario,
            codigo_tipo,
            nivel,
            titulo,
            mensaje,
            entidad_tipo,
            entidad_id,
            id_prospecto,
            dedupe_key,
            leida,
            fecha_leida,
            created_at,
            leible
        )
        values (
            %(rut_usuario)s,
            %(codigo_tipo)s,
            %(nivel)s,
            %(titulo)s,
            %(mensaje)s,
            %(entidad_tipo)s,
            %(entidad_id)s,
            %(id_prospecto)s,
            %(dedupe_key)s,
            false,
            null,
            %(created_at)s,
            true
        )
        on conflict (dedupe_key) do nothing
    '''
    params = {
        'rut_usuario': rut_asignado,
        'codigo_tipo': TIPO_ASIGNACION,
        'nivel': 'INFO',
        'titulo': titulo,
        'mensaje': mensaje,
        'entidad_tipo': entidad_tipo,
        'entidad_id': entidad_id,
        'id_prospecto': id_prospecto,
        'dedupe_key': f'{TIPO_ASIGNACION}:{entidad_tipo}:{entidad_id}:{rol}:{ahora.isoformat()}',
        'created_at': ahora,
        'leible': True,
    }

    cur.execute(query, params)
