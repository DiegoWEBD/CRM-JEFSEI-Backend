from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.historial_estado.repositorio_historial_estado import RepositorioHistorialEstado
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.historial_estado.adaptadores.dictrow_historial_estado_adapter import DictRowHistorialEstadoAdapter


class RepositorioHistorialEstadoPostgres(RepositorioHistorialEstado):

    def buscar_historial_prospecto(self, id_prospecto: int) -> list[HistorialEstado]:
         with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select EB_ANT.codigo as codigo_base_anterior, 
                    EB_ANT.nombre as nombre_base_anterior,
                    EB_ANT.dias_limite as dias_limite_base_anterior,
                    EP_ANT.dias_limite_particular as dias_limite_particular_anterior,
                    EB_ANT.accion as accion_base_anterior,
                    EB_ACT.codigo as codigo_base_actual, 
                    EB_ACT.nombre as nombre_base_actual,
                    EB_ACT.dias_limite as dias_limite_base_actual,
                    EP_ACT.dias_limite_particular as dias_limite_particular_actual,
                    EB_ACT.accion as accion_base_actual,
                    EB_SIG.codigo as codigo_siguiente_estado,
                    EB_SIG.nombre as nombre_siguiente_estado,
                    EB_SIG.dias_limite as dias_limite_siguiente_estado,
                    EB_SIG.accion as proxima_accion,
                    HE.fecha_registro, HE.motivo_cambio,
                    U.rut as rut_cambiado_por,
                    U.nombre as nombre_cambiado_por,
                    floor(extract(epoch from(current_timestamp - HE.fecha_registro)) / 86400) as dias_transcurridos
                    from Prospecto P
                    inner join ProcesoComercial PC
                    on PC.id_prospecto = P.id
                    inner join HistorialEstado HE
                    on HE.id_proceso_comercial = PC.id
                    inner join Usuario U
                    on HE.rut_cambiado_por = U.rut
                    left join EstadoParticular EP_ANT
                    on HE.id_estado_particular_anterior = EP_ANT.id
                    left join EstadoBase EB_ANT
                    on EP_ANT.codigo_estado_base = EB_ANT.codigo
                    inner join EstadoParticular EP_ACT
                    on HE.id_estado_particular_actual = EP_ACT.id
                    inner join EstadoBase EB_ACT
                    on EP_ACT.codigo_estado_base = EB_ACT.codigo
                    left join EstadoBase EB_SIG
                    on EB_ACT.codigo_siguiente_estado = EB_SIG.codigo
                    where P.id = %(id)s
                '''

                params = {
                    'id': id_prospecto
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowHistorialEstadoAdapter(row).to_historial_estado() for row in rows]