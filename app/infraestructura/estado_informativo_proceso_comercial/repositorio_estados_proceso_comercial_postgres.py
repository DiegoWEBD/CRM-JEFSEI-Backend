from psycopg import sql

from app.dominio.estado_informativo_proceso_comercial.estado_informativo_proceso_comercial import EstadoInformativoProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial
from app.dominio.etapa_proceso_comercial.etapa_proceso_comercial import EtapaProcesoComercial
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.estado_informativo_proceso_comercial.adaptadores.dictrow_transicion_estado_adapter import DictRowTransicionEstadoAdapter


class RepositorioEstadosProcesoComercialPostgres(RepositorioEstadosProcesoComercial):

    def _a_estado(self, row) -> EstadoInformativoProcesoComercial:
        return EstadoInformativoProcesoComercial(
            codigo=row['codigo'],
            nombre=row['nombre'],
            etapa=EtapaProcesoComercial(
                codigo=row['codigo_etapa'],
                nombre=row['nombre_etapa'],
                sigiuente_etapa=None,
            ),
            probabilidad_cierre=row['probabilidad_cierre'],
            rol_responsable=row['rol_responsable'],
            nombre_rol_responsable=row['nombre_rol_responsable'],
            cantidad_transiciones=row['cantidad_transiciones'],
        )

    def obtener_transiciones_manuales(self, codigo_estado: str) -> list[TransicionEstadoProcesoComercial]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select T.codigo_estado_origen,
                    T.codigo_estado_destino,
                    E.nombre as nombre_estado_destino,
                    T.es_manual,
                    T.es_principal,
                    T.accion_requerida
                    from TransicionEstadoProcesoComercial T
                    inner join EstadoInformativoProcesoComercial E
                    on T.codigo_estado_destino = E.codigo
                    where T.codigo_estado_origen = %(codigo_estado)s
                    and T.es_manual = true
                    order by T.es_principal desc, E.nombre
                '''

                params = {
                    'codigo_estado': codigo_estado
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowTransicionEstadoAdapter(row).to_transicion_estado_proceso_comercial() for row in rows]

    def obtener_todos(self, texto_busqueda: str | None = None) -> list[EstadoInformativoProcesoComercial]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                params: dict = {}
                condiciones: list[sql.Composable] = [sql.SQL('1 = 1')]

                if texto_busqueda:
                    condiciones.append(sql.SQL(
                        'UNACCENT(LOWER(E.nombre)) LIKE UNACCENT(LOWER(%(texto_busqueda)s))'
                        " OR UNACCENT(LOWER(ET.nombre)) LIKE UNACCENT(LOWER(%(texto_busqueda)s))"
                    ))
                    params['texto_busqueda'] = f'%{texto_busqueda}%'

                where_clause = sql.SQL(' WHERE ') + sql.SQL(' AND ').join(condiciones)

                query = sql.SQL('''
                    select E.codigo,
                    E.nombre,
                    E.codigo_etapa,
                    ET.nombre as nombre_etapa,
                    E.probabilidad_cierre,
                    E.rol_responsable,
                    R.nombre as nombre_rol_responsable,
                    (
                        select count(*)
                        from TransicionEstadoProcesoComercial T
                        where T.codigo_estado_origen = E.codigo
                    ) as cantidad_transiciones
                    from EstadoInformativoProcesoComercial E
                    inner join EtapaProcesoComercial ET
                    on E.codigo_etapa = ET.codigo
                    left join Rol R
                    on E.rol_responsable = R.codigo
                    {where_clause}
                    order by ET.orden nulls last,
                    E.codigo_etapa,
                    E.probabilidad_cierre asc,
                    E.nombre
                ''').format(where_clause=where_clause)

                cur.execute(query, params)
                rows = cur.fetchall()

                return [self._a_estado(row) for row in rows]

    def obtener_por_codigo(self, codigo: str) -> EstadoInformativoProcesoComercial | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select E.codigo,
                    E.nombre,
                    E.codigo_etapa,
                    ET.nombre as nombre_etapa,
                    E.probabilidad_cierre,
                    E.rol_responsable,
                    R.nombre as nombre_rol_responsable,
                    (
                        select count(*)
                        from TransicionEstadoProcesoComercial T
                        where T.codigo_estado_origen = E.codigo
                    ) as cantidad_transiciones
                    from EstadoInformativoProcesoComercial E
                    inner join EtapaProcesoComercial ET
                    on E.codigo_etapa = ET.codigo
                    left join Rol R
                    on E.rol_responsable = R.codigo
                    where E.codigo = %(codigo)s
                '''

                params = {'codigo': codigo}

                cur.execute(query, params)
                row = cur.fetchone()

                if not row:
                    return None

                return self._a_estado(row)

    def actualizar_configuracion(
        self, codigo: str, probabilidad_cierre: float
    ) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Los días límite no se tocan acá: viven en la transición
                # principal del estado.
                query = '''
                    update EstadoInformativoProcesoComercial
                    set probabilidad_cierre = %(probabilidad_cierre)s
                    where codigo = %(codigo)s
                '''

                params = {
                    'codigo': codigo,
                    'probabilidad_cierre': probabilidad_cierre,
                }

                cur.execute(query, params)
                conn.commit()

                return cur.rowcount > 0

    def obtener_transiciones(self, codigo_estado: str) -> list[TransicionEstadoProcesoComercial]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select T.codigo_estado_origen,
                    T.codigo_estado_destino,
                    EO.nombre as nombre_estado_origen,
                    ED.nombre as nombre_estado_destino,
                    T.es_manual,
                    T.es_principal,
                    T.accion_requerida,
                    T.dias_limite
                    from TransicionEstadoProcesoComercial T
                    inner join EstadoInformativoProcesoComercial EO
                    on T.codigo_estado_origen = EO.codigo
                    inner join EstadoInformativoProcesoComercial ED
                    on T.codigo_estado_destino = ED.codigo
                    where T.codigo_estado_origen = %(codigo_estado)s
                    order by T.es_principal desc, ED.nombre
                '''

                params = {'codigo_estado': codigo_estado}

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowTransicionEstadoAdapter(row).to_transicion_estado_proceso_comercial() for row in rows]

    def obtener_transicion(
        self, codigo_estado_origen: str, codigo_estado_destino: str
    ) -> TransicionEstadoProcesoComercial | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select T.codigo_estado_origen,
                    T.codigo_estado_destino,
                    EO.nombre as nombre_estado_origen,
                    ED.nombre as nombre_estado_destino,
                    T.es_manual,
                    T.es_principal,
                    T.accion_requerida,
                    T.dias_limite
                    from TransicionEstadoProcesoComercial T
                    inner join EstadoInformativoProcesoComercial EO
                    on T.codigo_estado_origen = EO.codigo
                    inner join EstadoInformativoProcesoComercial ED
                    on T.codigo_estado_destino = ED.codigo
                    where T.codigo_estado_origen = %(codigo_estado_origen)s
                    and T.codigo_estado_destino = %(codigo_estado_destino)s
                '''

                params = {
                    'codigo_estado_origen': codigo_estado_origen,
                    'codigo_estado_destino': codigo_estado_destino,
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if not row:
                    return None

                return DictRowTransicionEstadoAdapter(row).to_transicion_estado_proceso_comercial()

    def contar_transiciones_salida(self, codigo_estado_origen: str) -> int:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select count(*) as total
                    from TransicionEstadoProcesoComercial
                    where codigo_estado_origen = %(codigo_estado_origen)s
                '''

                params = {'codigo_estado_origen': codigo_estado_origen}

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return 0

                return row['total']

    def existe_transicion(self, codigo_estado_origen: str, codigo_estado_destino: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    SELECT EXISTS(
                        SELECT 1 FROM TransicionEstadoProcesoComercial
                        WHERE codigo_estado_origen = %(codigo_estado_origen)s
                        AND codigo_estado_destino = %(codigo_estado_destino)s
                    ) as existe
                '''

                params = {
                    'codigo_estado_origen': codigo_estado_origen,
                    'codigo_estado_destino': codigo_estado_destino,
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return False

                return row['existe']

    def crear_transicion(self, transicion: TransicionEstadoProcesoComercial) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # NOTA: las transiciones principales no se crean desde la
                # aplicación (el caso de uso las rechaza); se siembran por
                # migración. El índice único uq_transicion_principal es el
                # respaldo en base de datos.
                query = '''
                    insert into TransicionEstadoProcesoComercial
                    (codigo_estado_origen, codigo_estado_destino, es_principal, es_manual, accion_requerida, dias_limite)
                    values (%(codigo_estado_origen)s, %(codigo_estado_destino)s,
                            %(es_principal)s, %(es_manual)s, %(accion_requerida)s, %(dias_limite)s)
                '''

                params = {
                    'codigo_estado_origen': transicion.codigo_estado_origen,
                    'codigo_estado_destino': transicion.codigo_estado_destino,
                    'es_principal': transicion.es_principal,
                    'es_manual': transicion.es_manual,
                    'accion_requerida': transicion.accion_requerida,
                    'dias_limite': transicion.dias_limite,
                }

                cur.execute(query, params)
                conn.commit()

                return True

    def actualizar_transicion(self, transicion: TransicionEstadoProcesoComercial) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # En la principal, es_manual/accion_requerida quedan intactas y
                # solo cambia el días límite (SLA); en las secundarias al revés.
                query = '''
                    update TransicionEstadoProcesoComercial
                    set es_manual = %(es_manual)s,
                        accion_requerida = %(accion_requerida)s,
                        dias_limite = %(dias_limite)s
                    where codigo_estado_origen = %(codigo_estado_origen)s
                    and codigo_estado_destino = %(codigo_estado_destino)s
                '''

                params = {
                    'codigo_estado_origen': transicion.codigo_estado_origen,
                    'codigo_estado_destino': transicion.codigo_estado_destino,
                    'es_manual': transicion.es_manual,
                    'accion_requerida': transicion.accion_requerida,
                    'dias_limite': transicion.dias_limite,
                }

                cur.execute(query, params)
                conn.commit()

                return cur.rowcount > 0

    def eliminar_transicion(self, codigo_estado_origen: str, codigo_estado_destino: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    delete from TransicionEstadoProcesoComercial
                    where codigo_estado_origen = %(codigo_estado_origen)s
                    and codigo_estado_destino = %(codigo_estado_destino)s
                '''

                params = {
                    'codigo_estado_origen': codigo_estado_origen,
                    'codigo_estado_destino': codigo_estado_destino,
                }

                cur.execute(query, params)
                conn.commit()

                return cur.rowcount > 0
