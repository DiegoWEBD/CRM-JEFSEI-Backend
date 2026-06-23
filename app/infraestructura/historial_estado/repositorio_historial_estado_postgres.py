from app.dominio.historial_estado.historial_estado import HistorialEstado
from app.dominio.historial_estado.repositorio_historial_estado import RepositorioHistorialEstado
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.historial_estado.adaptadores.dictrow_historial_estado_adapter import DictRowHistorialEstadoAdapter


class RepositorioHistorialEstadoPostgres(RepositorioHistorialEstado):

    def buscar_historial_proceso_comercial(self, id_proceso_comercial: int) -> list[HistorialEstado]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                    
                # Registro de historial

                query = '''
                    select EI.codigo_etapa,
                    EPC.nombre as etapa,
                    EI.codigo as codigo_estado,
                    EI.nombre as estado,
                    HI.fecha_registro,
                    current_date - HI.fecha_registro::date as dias_transcurridos,
                    HI.observacion,
                    HI.rut_registrado_por,
                    U.nombre as registrado_por
                    from HistorialEstadoInformativoProcesoComercial HI
                    inner join EstadoInformativoProcesoComercial EI
                    on HI.codigo_estado = EI.codigo
                    inner join EtapaProcesoComercial EPC
                    on EI.codigo_etapa = EPC.codigo
                    inner join Usuario U
                    on HI.rut_registrado_por = U.rut
                    where HI.id_proceso_comercial = %(id_proceso_comercial)s
                    order by HI.fecha_registro asc
                '''
                
                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowHistorialEstadoAdapter(row).to_historial_estado() for row in rows]