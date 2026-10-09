from app.dominio.estado_informativo_proceso_comercial.repositorio_estados_proceso_comercial import RepositorioEstadosProcesoComercial
from app.dominio.estado_informativo_proceso_comercial.transicion_estado_proceso_comercial import TransicionEstadoProcesoComercial
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.estado_informativo_proceso_comercial.adaptadores.dictrow_transicion_estado_adapter import DictRowTransicionEstadoAdapter


class RepositorioEstadosProcesoComercialPostgres(RepositorioEstadosProcesoComercial):

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
