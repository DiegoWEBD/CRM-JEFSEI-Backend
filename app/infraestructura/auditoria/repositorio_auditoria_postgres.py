from datetime import datetime
from typing import Any, Optional

from psycopg import Connection, sql
from psycopg.rows import DictRow
from psycopg.types.json import Jsonb

from app.dominio.auditoria.auditoria_evento import AuditoriaEvento
from app.dominio.auditoria.enums import Categoria, Resultado, TipoEvento
from app.dominio.auditoria.repositorio_auditoria import RepositorioAuditoria
from app.infraestructura.db.conexion import obtener_conexion

# psycopg no sabe adaptar un dict ni un string a inet/UUID por sí solo: sin
# estos envoltorios la escritura falla con "cannot adapt type 'dict'" y el
# evento se pierde (o, si es crítico, tumba el request).
def _jsonb(valor):
    return Jsonb(valor) if valor is not None else None


def _uuid(valor):
    return valor if valor is None else str(valor)

COLUMNAS = '''
    A.id, A.fecha_hora, A.rut_usuario, A.tipo_evento, A.categoria, A.resultado,
    A.metodo_http, A.endpoint, A.path, A.ip_origen, A.user_agent, A.origin,
    A.referer, A.request_id, A.id_sesion, A.recurso_tipo, A.recurso_id,
    A.descripcion, A.datos_antes, A.datos_despues, A.cambios, A.metadata,
    A.duracion_ms, A.status_http, A.error_codigo, A.created_at
'''

INSERT = '''
    insert into AuditoriaEvento (
        fecha_hora, rut_usuario, tipo_evento, categoria, resultado,
        metodo_http, endpoint, path, ip_origen, user_agent, origin, referer,
        request_id, id_sesion, recurso_tipo, recurso_id, descripcion,
        datos_antes, datos_despues, cambios, metadata,
        duracion_ms, status_http, error_codigo
    ) values (
        coalesce(%(fecha_hora)s, current_timestamp),
        %(rut_usuario)s, %(tipo_evento)s, %(categoria)s, %(resultado)s,
        %(metodo_http)s, %(endpoint)s, %(path)s, %(ip_origen)s::inet, %(user_agent)s,
        %(origin)s, %(referer)s, %(request_id)s, %(id_sesion)s::uuid,
        %(recurso_tipo)s, %(recurso_id)s, %(descripcion)s,
        %(datos_antes)s, %(datos_despues)s, %(cambios)s, %(metadata)s,
        %(duracion_ms)s, %(status_http)s, %(error_codigo)s
    )
    returning id
'''


class RepositorioAuditoriaPostgres(RepositorioAuditoria):

    def registrar(
        self,
        evento: AuditoriaEvento,
        conn: Optional[Connection[DictRow]] = None,
    ) -> AuditoriaEvento:
        params = {
            'fecha_hora': evento.fecha_hora,
            'rut_usuario': evento.rut_usuario,
            'tipo_evento': evento.tipo_evento,
            'categoria': evento.categoria,
            'resultado': evento.resultado,
            'metodo_http': evento.metodo_http,
            'endpoint': evento.endpoint,
            'path': evento.path,
            'ip_origen': _uuid(evento.ip_origen),
            'user_agent': evento.user_agent,
            'origin': evento.origin,
            'referer': evento.referer,
            'request_id': evento.request_id,
            'id_sesion': _uuid(evento.id_sesion),
            'recurso_tipo': evento.recurso_tipo,
            'recurso_id': evento.recurso_id,
            'descripcion': evento.descripcion,
            'datos_antes': _jsonb(evento.datos_antes),
            'datos_despues': _jsonb(evento.datos_despues),
            'cambios': _jsonb(evento.cambios),
            'metadata': _jsonb(evento.metadata),
            'duracion_ms': evento.duracion_ms,
            'status_http': evento.status_http,
            'error_codigo': evento.error_codigo,
        }

        if conn is not None:
            with conn.cursor() as cur:
                cur.execute(INSERT, params)
                fila = cur.fetchone()
        else:
            with obtener_conexion() as conexion:
                with conexion.cursor() as cur:
                    cur.execute(INSERT, params)
                    fila = cur.fetchone()

        if fila:
            evento.id = fila['id']
        return evento

    def obtener_por_id(self, id_evento: int) -> AuditoriaEvento | None:
        query = f'select {COLUMNAS} from AuditoriaEvento A where A.id = %(id_evento)s'
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(query, {'id_evento': id_evento})
                fila = cur.fetchone()
        return _a_entidad(fila) if fila else None

    def obtener_paginado(
        self,
        fecha_desde: datetime | None,
        fecha_hasta: datetime | None,
        rut_usuario: str | None,
        ip_origen: str | None,
        tipo_evento: TipoEvento | None,
        categoria: Categoria | None,
        resultado: Resultado | None,
        recurso_tipo: str | None,
        recurso_id: str | None,
        request_id: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[AuditoriaEvento], int]:
        condiciones: list[sql.Composable] = []
        params: dict[str, Any] = {}

        # (condición parametrizada, valor, nombre del parámetro). El nombre va
        # explícito: no se deduce parseando el texto de la condición.
        filtros = (
            ('A.fecha_hora >= %(fecha_desde)s', fecha_desde, 'fecha_desde'),
            ('A.fecha_hora < %(fecha_hasta)s', fecha_hasta, 'fecha_hasta'),
            ('A.rut_usuario = %(rut_usuario)s', rut_usuario, 'rut_usuario'),
            ('A.ip_origen = %(ip_origen)s::inet', ip_origen, 'ip_origen'),
            ('A.tipo_evento = %(tipo_evento)s', tipo_evento, 'tipo_evento'),
            ('A.categoria = %(categoria)s', categoria, 'categoria'),
            ('A.resultado = %(resultado)s', resultado, 'resultado'),
            ('A.recurso_tipo = %(recurso_tipo)s', recurso_tipo, 'recurso_tipo'),
            ('A.recurso_id = %(recurso_id)s', recurso_id, 'recurso_id'),
            ('A.request_id = %(request_id)s::uuid', request_id, 'request_id'),
        )
        for condicion, valor, nombre in filtros:
            if valor is not None:
                condiciones.append(sql.SQL(condicion))
                params[nombre] = valor

        where = (
            sql.SQL(' where ') + sql.SQL(' and ').join(condiciones)
            if condiciones
            else sql.SQL('')
        )

        # La paginación se acota en servidor: nunca se devuelve la tabla entera.
        pagina = max(pagina, 1)
        tamano_pagina = min(max(tamano_pagina, 1), 200)
        params['limite'] = tamano_pagina
        params['offset'] = (pagina - 1) * tamano_pagina

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL('select count(*) as total from AuditoriaEvento A')
                    + where,
                    params,
                )
                total = cur.fetchone()['total']

                cur.execute(
                    sql.SQL(
                        f'select {COLUMNAS} from AuditoriaEvento A'
                    ) + where
                    + sql.SQL(' order by A.fecha_hora desc, A.id desc'
                              ' limit %(limite)s offset %(offset)s'),
                    params,
                )
                filas = cur.fetchall()

        return [_a_entidad(f) for f in filas], total

    def obtener_por_recurso(
        self,
        recurso_tipo: str,
        recurso_id: str,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[AuditoriaEvento], int]:
        pagina = max(pagina, 1)
        tamano_pagina = min(max(tamano_pagina, 1), 200)

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    select count(*) as total
                    from AuditoriaEvento
                    where recurso_tipo = %s and recurso_id = %s
                ''', (recurso_tipo, recurso_id))
                total = cur.fetchone()['total']

                cur.execute('''
                    select ''' + COLUMNAS + '''
                    from AuditoriaEvento A
                    where A.recurso_tipo = %s and A.recurso_id = %s
                    order by A.fecha_hora desc, A.id desc
                    limit %s offset %s
                ''', (recurso_tipo, recurso_id, tamano_pagina,
                      (pagina - 1) * tamano_pagina))
                filas = cur.fetchall()

        return [_a_entidad(f) for f in filas], total


def _a_entidad(fila: DictRow) -> AuditoriaEvento:
    return AuditoriaEvento(
        id=fila['id'],
        fecha_hora=fila['fecha_hora'],
        rut_usuario=fila['rut_usuario'],
        tipo_evento=TipoEvento(fila['tipo_evento']),
        categoria=Categoria(fila['categoria']),
        resultado=Resultado(fila['resultado']),
        request_id=str(fila['request_id']),
        metodo_http=fila['metodo_http'],
        endpoint=fila['endpoint'],
        path=fila['path'],
        ip_origen=str(fila['ip_origen']) if fila['ip_origen'] else None,
        user_agent=fila['user_agent'],
        origin=fila['origin'],
        referer=fila['referer'],
        id_sesion=str(fila['id_sesion']) if fila['id_sesion'] else None,
        recurso_tipo=fila['recurso_tipo'],
        recurso_id=fila['recurso_id'],
        descripcion=fila['descripcion'],
        datos_antes=fila['datos_antes'],
        datos_despues=fila['datos_despues'],
        cambios=fila['cambios'],
        metadata=fila['metadata'],
        duracion_ms=fila['duracion_ms'],
        status_http=fila['status_http'],
        error_codigo=fila['error_codigo'],
        created_at=fila['created_at'],
    )
