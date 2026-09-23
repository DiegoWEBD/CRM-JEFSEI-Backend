from datetime import datetime, timezone

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
                    PC.cerrado
                    from ProcesoComercial PC
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
                    where PC.cerrado = false
                '''

                cur.execute(query)
                rows = cur.fetchall()

                return [DictRowProcesoAlertableSlaAdapter(row).to_proceso_alertable_sla() for row in rows]

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
                        url_destino,
                        dedupe_key,
                        leida,
                        fecha_leida,
                        created_at
                    )
                    values (
                        %(rut_usuario)s,
                        %(codigo_tipo)s,
                        %(nivel)s,
                        %(titulo)s,
                        %(mensaje)s,
                        %(entidad_tipo)s,
                        %(entidad_id)s,
                        %(url_destino)s,
                        %(dedupe_key)s,
                        false,
                        null,
                        %(created_at)s
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
                    'url_destino': notificacion.url_destino,
                    'dedupe_key': notificacion.dedupe_key,
                    'created_at': notificacion.created_at or datetime.now(tz=timezone.utc),
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row:
                    notificacion.id = row['id']
                    return True

                return False

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
                condiciones = ['N.rut_usuario = %(rut_usuario)s']
                params: dict = {'rut_usuario': rut_usuario}

                if no_leidas is not None:
                    condiciones.append('N.leida = %(no_leidas)s')
                    params['no_leidas'] = not no_leidas

                if nivel:
                    condiciones.append('N.nivel = %(nivel)s')
                    params['nivel'] = nivel

                if codigo_tipo:
                    condiciones.append('N.codigo_tipo = %(codigo_tipo)s')
                    params['codigo_tipo'] = codigo_tipo

                where_sql = ' where ' + ' and '.join(condiciones)

                count_query = 'select count(*) as total from Notificacion N' + where_sql
                cur.execute(count_query, params)
                total = cur.fetchone()['total']

                offset = (pagina - 1) * tamano_pagina

                data_query = '''
                    select N.id,
                    N.rut_usuario,
                    N.codigo_tipo,
                    N.nivel,
                    N.titulo,
                    N.mensaje,
                    N.entidad_tipo,
                    N.entidad_id,
                    N.url_destino,
                    N.dedupe_key,
                    N.leida,
                    N.fecha_leida,
                    N.created_at
                    from Notificacion N
                ''' + where_sql + '''
                    order by N.created_at desc
                    limit %(tamano_pagina)s offset %(offset)s
                '''
                data_params = {**params, 'tamano_pagina': tamano_pagina, 'offset': offset}
                cur.execute(data_query, data_params)
                rows = cur.fetchall()

                return [DictRowNotificacionAdapter(row).to_notificacion() for row in rows], total

    def obtener_contador_no_leidas(self, rut_usuario: str) -> int:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = '''
                    select count(*) as total
                    from Notificacion
                    where rut_usuario = %(rut_usuario)s
                    and leida = false
                '''
                cur.execute(query, {'rut_usuario': rut_usuario})

                return cur.fetchone()['total']

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
                '''
                params = {
                    'rut_usuario': rut_usuario,
                    'fecha_leida': datetime.now(tz=timezone.utc),
                }

                cur.execute(query, params)

                return cur.rowcount
