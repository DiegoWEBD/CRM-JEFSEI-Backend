from datetime import datetime, timezone

from psycopg import sql

from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.notificacion.notificacion import Notificacion
from app.dominio.notificacion.proceso_alertable_sla import ProcesoAlertableSla
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.notificacion.adaptadores.dictrow_notificacion_adapter import DictRowNotificacionAdapter
from app.infraestructura.notificacion.adaptadores.dictrow_proceso_alertable_sla_adapter import DictRowProcesoAlertableSlaAdapter


class RepositorioNotificacionesPostgres(RepositorioNotificaciones):

    def obtener_procesos_alertables(self) -> list[ProcesoAlertableSla]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select PC.id as id_proceso_comercial,
                    PRO.nombre as nombre_producto,
                    PC.id_prospecto,
                    EI.codigo as codigo_estado,
                    EI.nombre as nombre_estado,
                    EPC.nombre as nombre_etapa,
                    PR.nombre_riesgo as nombre_prospecto,
                    HI.fecha_registro as fecha_ingreso_estado,
                    EI.dias_limite,
                    EPC.dias_limite as dias_limite_etapa,
                    EI.rol_responsable,
                    PC.rut_ej_comercial,
                    PC.rut_ej_evaluacion,
                    PC.cerrado,
                    T.codigo_estado_destino as codigo_siguiente_estado,
                    EI_SIGUIENTE.nombre as nombre_siguiente_estado,
                    EI_SIGUIENTE.rol_responsable as rol_responsable_siguiente,
                    T.accion_requerida
                    from ProcesoComercial PC
                    inner join Producto PRO
                    on PC.id_producto = PRO.id
                    inner join Prospecto PR
                    on PC.id_prospecto = PR.id
                    inner join HistorialEstadoInformativoProcesoComercial HI
                    on PC.id = HI.id_proceso_comercial
                    and HI.fecha_registro = (
                        select max(HI2.fecha_registro)
                        from HistorialEstadoInformativoProcesoComercial HI2
                        where HI2.id_proceso_comercial = PC.id
                    )
                    inner join EstadoInformativoProcesoComercial EI
                    on HI.codigo_estado = EI.codigo
                    and EI.codigo = PC.codigo_estado_actual
                    inner join EtapaProcesoComercial EPC
                    on EI.codigo_etapa = EPC.codigo
                    left join TransicionEstadoProcesoComercial T
                    on T.codigo_estado_origen = EI.codigo
                    and T.es_principal = true
                    left join EstadoInformativoProcesoComercial EI_SIGUIENTE
                    on EI_SIGUIENTE.codigo = T.codigo_estado_destino
                    where PC.cerrado = false
                '''

                cur.execute(query)
                rows = cur.fetchall()

                return [DictRowProcesoAlertableSlaAdapter(row).to_proceso_alertable_sla() for row in rows]

    def obtener_ruts_por_roles(self, roles: list[str]) -> dict[str, list[str]]:
        """Devuelve {rol: [rut1, rut2, ...]} para los roles dados.

        Solo incluye usuarios habilitados y no eliminados.
        Se usa para el fan-out de alertas SLA a roles sin asignación
        por proceso (p.ej. GERENTE_COMERCIAL).
        """
        if not roles:
            return {}

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select RU.codigo_rol, U.rut
                    from RolUsuario RU
                    inner join Usuario U on U.rut = RU.rut_usuario
                    where RU.codigo_rol = any(%(roles)s)
                    and U.habilitado = true
                    and U.eliminado = false
                '''
                cur.execute(query, {'roles': roles})
                rows = cur.fetchall()

                resultado: dict[str, list[str]] = {r: [] for r in roles}
                for row in rows:
                    resultado[row['codigo_rol']].append(row['rut'])
                return resultado

    def registrar(self, notificacion: Notificacion) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
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
                        %(leible)s
                    )
                    on conflict (dedupe_key) do nothing
                    returning id
                '''
                params = {
                    'rut_usuario': notificacion.rut_usuario,
                    'codigo_tipo': notificacion.codigo_tipo,
                    'nivel': notificacion.nivel,
                    'titulo': notificacion.titulo,
                    'mensaje': notificacion.mensaje,
                    'entidad_tipo': notificacion.entidad_tipo,
                    'entidad_id': notificacion.entidad_id,
                    'id_prospecto': notificacion.id_prospecto,
                    'dedupe_key': notificacion.dedupe_key,
                    'created_at': notificacion.created_at or datetime.now(tz=timezone.utc),
                    'leible': notificacion.leible,
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row:
                    notificacion.id = row['id']
                    return True

                return False

    def existe_alerta_proceso(self, codigo_tipo: str, id_proceso: int, rut_usuario: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select exists(
                        select 1 from Notificacion
                        where codigo_tipo = %(codigo_tipo)s
                        and entidad_tipo = 'PROCESO_COMERCIAL'
                        and entidad_id = %(id_proceso)s
                        and rut_usuario = %(rut_usuario)s
                    ) as existe
                '''
                params = {
                    'codigo_tipo': codigo_tipo,
                    'id_proceso': id_proceso,
                    'rut_usuario': rut_usuario,
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return bool(row['existe']) if row else False

    def _construir_where(
        self,
        rut_usuario: str,
        no_leidas: bool | None,
        nivel: str | None,
        codigo_tipo: str | None,
        params: dict,
    ) -> sql.Composable:
        condiciones: list[sql.Composable] = [sql.SQL('N.rut_usuario = %(rut_usuario)s')]
        params['rut_usuario'] = rut_usuario

        if no_leidas is not None:
            condiciones.append(sql.SQL('N.leida = %(no_leidas)s'))
            params['no_leidas'] = not no_leidas

        if nivel:
            condiciones.append(sql.SQL('N.nivel = %(nivel)s'))
            params['nivel'] = nivel

        if codigo_tipo:
            condiciones.append(sql.SQL('N.codigo_tipo = %(codigo_tipo)s'))
            params['codigo_tipo'] = codigo_tipo

        return sql.SQL(' WHERE ') + sql.SQL(' AND ').join(condiciones)

    def obtener_paginado(
        self,
        rut_usuario: str,
        no_leidas: bool | None,
        nivel: str | None,
        codigo_tipo: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[Notificacion], int]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                params: dict = {}
                where_clause = self._construir_where(
                    rut_usuario, no_leidas, nivel, codigo_tipo, params
                )

                count_query = sql.SQL('''
                    select count(*) as total
                    from Notificacion N
                    {where_clause}
                ''').format(where_clause=where_clause)
                cur.execute(count_query, params)
                total = cur.fetchone()['total'] # type: ignore

                offset = (pagina - 1) * tamano_pagina

                data_query = sql.SQL('''
                    select N.id,
                    N.rut_usuario,
                    N.codigo_tipo,
                    N.nivel,
                    N.titulo,
                    N.mensaje,
                    N.entidad_tipo,
                    N.entidad_id,
                    N.id_prospecto,
                    N.dedupe_key,
                    N.leida,
                    N.fecha_leida,
                    N.created_at,
                    N.leible
                    from Notificacion N
                    {where_clause}
                    order by N.created_at desc
                    limit %(tamano_pagina)s offset %(offset)s
                ''').format(where_clause=where_clause)
                data_params = {**params, 'tamano_pagina': tamano_pagina, 'offset': offset}
                cur.execute(data_query, data_params)
                rows = cur.fetchall()

                return [DictRowNotificacionAdapter(row).to_notificacion() for row in rows], total

    def contar(self, rut_usuario: str, leidas: bool, leibles: bool) -> int:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select count(*) as total
                    from Notificacion
                    where rut_usuario = %(rut_usuario)s
                    and leida = %(leidas)s
                    and leible = %(leibles)s
                '''
                cur.execute(query, {'rut_usuario': rut_usuario, 'leidas': leidas, 'leibles': leibles})
                return cur.fetchone()['total'] # type: ignore   

    def buscar(self, id_notificacion: int) -> Notificacion | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select N.id,
                    N.rut_usuario,
                    N.codigo_tipo,
                    N.nivel,
                    N.titulo,
                    N.mensaje,
                    N.entidad_tipo,
                    N.entidad_id,
                    N.id_prospecto,
                    N.dedupe_key,
                    N.leida,
                    N.fecha_leida,
                    N.created_at,
                    N.leible
                    from Notificacion N
                    where N.id = %(id)s
                '''
                cur.execute(query, {'id': id_notificacion})
                row = cur.fetchone()

                if row is None:
                    return None

                return DictRowNotificacionAdapter(row).to_notificacion()

    def marcar_leida(self, id_notificacion: int, rut_usuario: str) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    update Notificacion
                    set leida = true,
                    fecha_leida = %(fecha_leida)s
                    where id = %(id)s
                    and rut_usuario = %(rut_usuario)s
                    and leida = false
                    returning id
                '''
                params = {
                    'id': id_notificacion,
                    'rut_usuario': rut_usuario,
                    'fecha_leida': datetime.now(tz=timezone.utc),
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    # O no existe o pertenece a otro usuario
                    existe_query = '''
                        select 1 from Notificacion
                        where id = %(id)s
                    '''
                    cur.execute(existe_query, {'id': id_notificacion})

                    if cur.fetchone() is None:
                        raise RecursoNoEncontradoException('Notificación no encontrada')

    def marcar_todas_leidas(self, rut_usuario: str) -> int:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    update Notificacion
                    set leida = true,
                    fecha_leida = %(fecha_leida)s
                    where rut_usuario = %(rut_usuario)s
                    and leida = false
                    and leible = true
                '''
                params = {
                    'rut_usuario': rut_usuario,
                    'fecha_leida': datetime.now(tz=timezone.utc),
                }

                cur.execute(query, params)

                return cur.rowcount
