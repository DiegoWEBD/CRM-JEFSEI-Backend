from datetime import datetime

from psycopg import sql
from psycopg.rows import DictRow

from app.dominio.auditoria.registro_auditoria import RegistroAuditoria
from app.dominio.auditoria.repositorio_auditoria import RepositorioAuditoria
from app.infraestructura.auditoria.adaptadores.dictrow_registro_auditoria_adapter import DictRowRegistroAuditoriaAdapter
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioAuditoriaPostgres(RepositorioAuditoria):

    def registrar(self, registro: RegistroAuditoria) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    insert into RegistroAuditoria(
                        fecha_registro, categoria, evento, resultado, estado_http,
                        rut_usuario, nombre_usuario, ip_origen, user_agent,
                        id_peticion, metodo, ruta, entidad_tipo, entidad_id,
                        detalle, duracion_ms
                    )
                    values(
                        %(fecha_registro)s, %(categoria)s, %(evento)s, %(resultado)s, %(estado_http)s,
                        %(rut_usuario)s, %(nombre_usuario)s, %(ip_origen)s, %(user_agent)s,
                        %(id_peticion)s, %(metodo)s, %(ruta)s, %(entidad_tipo)s, %(entidad_id)s,
                        %(detalle)s, %(duracion_ms)s
                    )
                '''
                params = {
                    'fecha_registro': registro.fecha_registro,
                    'categoria': registro.categoria,
                    'evento': registro.evento,
                    'resultado': registro.resultado,
                    'estado_http': registro.estado_http,
                    'rut_usuario': registro.rut_usuario,
                    'nombre_usuario': registro.nombre_usuario,
                    'ip_origen': registro.ip_origen,
                    'user_agent': registro.user_agent,
                    'id_peticion': registro.id_peticion,
                    'metodo': registro.metodo,
                    'ruta': registro.ruta,
                    'entidad_tipo': registro.entidad_tipo,
                    'entidad_id': registro.entidad_id,
                    'detalle': registro.detalle,
                    'duracion_ms': registro.duracion_ms,
                }
                cur.execute(query, params)

    def _construir_where(
        self,
        categoria: str | None,
        evento: str | None,
        rut_usuario: str | None,
        ip_origen: str | None,
        entidad_tipo: str | None,
        fecha_desde: datetime | None,
        fecha_hasta: datetime | None,
        texto_busqueda: str | None,
        params: dict,
    ):
        condiciones = []

        if categoria:
            condiciones.append(sql.SQL('RA.categoria = %(categoria)s'))
            params['categoria'] = categoria

        if evento:
            condiciones.append(sql.SQL('RA.evento = %(evento)s'))
            params['evento'] = evento

        if rut_usuario:
            condiciones.append(sql.SQL(
                'UNACCENT(LOWER(RA.rut_usuario)) LIKE UNACCENT(LOWER(%(rut_usuario)s))'
            ))
            params['rut_usuario'] = f'%{rut_usuario}%'

        if ip_origen:
            condiciones.append(sql.SQL('RA.ip_origen LIKE %(ip_origen)s'))
            params['ip_origen'] = f'%{ip_origen}%'

        if entidad_tipo:
            condiciones.append(sql.SQL('RA.entidad_tipo = %(entidad_tipo)s'))
            params['entidad_tipo'] = entidad_tipo

        if fecha_desde:
            condiciones.append(sql.SQL('RA.fecha_registro >= %(fecha_desde)s'))
            params['fecha_desde'] = fecha_desde

        if fecha_hasta:
            condiciones.append(sql.SQL('RA.fecha_registro <= %(fecha_hasta)s'))
            params['fecha_hasta'] = fecha_hasta

        if texto_busqueda:
            condiciones.append(sql.SQL(
                '('
                'UNACCENT(LOWER(RA.rut_usuario)) LIKE UNACCENT(LOWER(%(texto_busqueda)s)) '
                'OR UNACCENT(LOWER(RA.nombre_usuario)) LIKE UNACCENT(LOWER(%(texto_busqueda)s)) '
                'OR UNACCENT(LOWER(RA.evento)) LIKE UNACCENT(LOWER(%(texto_busqueda)s)) '
                'OR UNACCENT(LOWER(RA.ruta)) LIKE UNACCENT(LOWER(%(texto_busqueda)s)) '
                'OR UNACCENT(LOWER(RA.ip_origen)) LIKE UNACCENT(LOWER(%(texto_busqueda)s)) '
                'OR UNACCENT(LOWER(RA.detalle)) LIKE UNACCENT(LOWER(%(texto_busqueda)s))'
                ')'
            ))
            params['texto_busqueda'] = f'%{texto_busqueda}%'

        if not condiciones:
            return sql.SQL('')

        return sql.SQL(' WHERE ') + sql.SQL(' AND ').join(condiciones)

    def obtener_paginados(
        self,
        categoria: str | None,
        evento: str | None,
        rut_usuario: str | None,
        ip_origen: str | None,
        entidad_tipo: str | None,
        fecha_desde: datetime | None,
        fecha_hasta: datetime | None,
        texto_busqueda: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[RegistroAuditoria], int]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                params: dict = {}
                where_clause = self._construir_where(
                    categoria, evento, rut_usuario, ip_origen, entidad_tipo,
                    fecha_desde, fecha_hasta, texto_busqueda, params,
                )

                count_query = sql.SQL('''
                    SELECT COUNT(*) as total
                    FROM RegistroAuditoria RA
                    {where_clause}
                ''').format(where_clause=where_clause)
                cur.execute(count_query, params)
                total = cur.fetchone()['total'] # type: ignore

                offset = (pagina - 1) * tamano_pagina

                data_query = sql.SQL('''
                    SELECT RA.id, RA.fecha_registro, RA.categoria, RA.evento, RA.resultado,
                    RA.estado_http, RA.rut_usuario, RA.nombre_usuario, RA.ip_origen,
                    RA.user_agent, RA.id_peticion, RA.metodo, RA.ruta, RA.entidad_tipo,
                    RA.entidad_id, RA.detalle, RA.duracion_ms
                    FROM RegistroAuditoria RA
                    {where_clause}
                    ORDER BY RA.fecha_registro DESC, RA.id DESC
                    LIMIT %(tamano_pagina)s OFFSET %(offset)s
                ''').format(where_clause=where_clause)
                page_params = {**params, "tamano_pagina": tamano_pagina, "offset": offset}
                cur.execute(data_query, page_params)
                rows: list[DictRow] = cur.fetchall() # type: ignore

                registros = [DictRowRegistroAuditoriaAdapter(row).to_registro_auditoria() for row in rows]

                return registros, total
