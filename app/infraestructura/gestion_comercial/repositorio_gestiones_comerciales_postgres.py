from datetime import datetime, timezone

from psycopg import sql

from app.dominio.gestion_comercial.gestion_comercial import GestionComercial
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.gestion_comercial.adaptadores.dictrow_gestion_comercial_adapter import DictRowGestionComercialAdapter


class RepositorioGestionesComercialesPostgres(RepositorioGestionesComerciales):

    def registrar(
        self,
        tipo: str,
        rut_usuario: str,
        id_prospecto: int,
        titulo: str,
        estado_contacto: str | None,
        observacion: str | None,
        fecha_gestion: str,
    ) -> GestionComercial:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                created_at = datetime.now(timezone.utc)

                cur.execute(
                    '''
                    insert into GestionComercial (tipo, rut_usuario, id_prospecto, titulo, estado_contacto, observacion, created_at, fecha_gestion)
                    values (%(tipo)s, %(rut_usuario)s, %(id_prospecto)s, %(titulo)s, %(estado_contacto)s, %(observacion)s, %(created_at)s, %(fecha_gestion)s::timestamptz)
                    returning id
                    ''',
                    {
                        'tipo': tipo,
                        'rut_usuario': rut_usuario,
                        'id_prospecto': id_prospecto,
                        'titulo': titulo,
                        'estado_contacto': estado_contacto,
                        'observacion': observacion,
                        'created_at': created_at,
                        'fecha_gestion': fecha_gestion,
                    },
                )
                row = cur.fetchone()
                if row is None:
                    raise RuntimeError('No se pudo crear la gestión comercial')
                id_creado: int = row['id']

        return self._buscar_por_id(id_creado)

    def obtener_todas(self, id_prospecto: int | None = None, rut_usuario: str | None = None) -> list[GestionComercial]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                params: dict = {}
                condiciones: list[sql.Composable] = []

                if id_prospecto is not None:
                    condiciones.append(sql.SQL('GC.id_prospecto = %(id_prospecto)s'))
                    params['id_prospecto'] = id_prospecto

                if rut_usuario is not None:
                    condiciones.append(sql.SQL('''
                        (
                            exists (
                                select 1 from Prospecto P
                                where P.id = GC.id_prospecto
                                and (P.rut_ej_comercial_asignado = %(rut_usuario)s
                                     or P.rut_ej_evaluacion_asignado = %(rut_usuario)s)
                            )
                            or exists (
                                select 1 from Cliente C
                                where C.id_prospecto = GC.id_prospecto
                                and (C.rut_ej_renovacion_asignado = %(rut_usuario)s
                                     or C.rut_as_renovacion_asignado = %(rut_usuario)s
                                     or C.rut_ej_cobranza_asignado = %(rut_usuario)s)
                            )
                        )
                    '''))
                    params['rut_usuario'] = rut_usuario

                if condiciones:
                    where_clause = sql.SQL(' where ') + sql.SQL(' and ').join(condiciones)
                else:
                    where_clause = sql.SQL('')

                query = sql.SQL('''
                    select
                        GC.id,
                        GC.tipo,
                        GC.rut_usuario,
                        U.nombre as nombre_ejecutivo,
                        GC.id_prospecto,
                        PR.nombre_riesgo as nombre_cliente,
                        GC.titulo,
                        GC.estado_contacto,
                        GC.observacion,
                        GC.created_at,
                        GC.fecha_gestion
                    from GestionComercial GC
                    left join Usuario U on GC.rut_usuario = U.rut
                    left join Prospecto PR on GC.id_prospecto = PR.id
                    {where_clause}
                    order by GC.fecha_gestion desc
                ''').format(where_clause=where_clause)

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowGestionComercialAdapter(row).to_gestion_comercial() for row in rows]

    def obtener_ultima(self, id_prospecto: int) -> GestionComercial | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select
                        GC.id,
                        GC.tipo,
                        GC.rut_usuario,
                        U.nombre as nombre_ejecutivo,
                        GC.id_prospecto,
                        PR.nombre_riesgo as nombre_cliente,
                        GC.titulo,
                        GC.estado_contacto,
                        GC.observacion,
                        GC.created_at,
                        GC.fecha_gestion
                    from GestionComercial GC
                    left join Usuario U on GC.rut_usuario = U.rut
                    left join Prospecto PR on GC.id_prospecto = PR.id
                    where GC.id_prospecto = %(id_prospecto)s
                    order by GC.created_at desc
                    limit 1
                    ''',
                    {'id_prospecto': id_prospecto},
                )
                row = cur.fetchone()

                return DictRowGestionComercialAdapter(row).to_gestion_comercial() if row else None

    def _buscar_por_id(self, id: int) -> GestionComercial:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select
                        GC.id,
                        GC.tipo,
                        GC.rut_usuario,
                        U.nombre as nombre_ejecutivo,
                        GC.id_prospecto,
                        PR.nombre_riesgo as nombre_cliente,
                        GC.titulo,
                        GC.estado_contacto,
                        GC.observacion,
                        GC.created_at,
                        GC.fecha_gestion
                    from GestionComercial GC
                    left join Usuario U on GC.rut_usuario = U.rut
                    left join Prospecto PR on GC.id_prospecto = PR.id
                    where GC.id = %(id)s
                    ''',
                    {'id': id},
                )
                row = cur.fetchone()
                if row is None:
                    raise RuntimeError(f'Gestión comercial con id {id} no encontrada después de crear')
                return DictRowGestionComercialAdapter(row).to_gestion_comercial()
