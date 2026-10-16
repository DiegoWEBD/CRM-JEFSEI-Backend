from app.dominio.historial_estado.historial_estado_proceso_comercial import HistorialEstadoProcesoComercial
from app.dominio.historial_estado.repositorio_historial_estado_procesos_comerciales import RepositorioHistorialEstadoProcesosComerciales
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioHistorialEstadoProcesosComercialesPostgres(RepositorioHistorialEstadoProcesosComerciales):

    def registrar(self, historial: HistorialEstadoProcesoComercial) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # 1. Insertar en historial (patrón anti-duplicado del último estado)

                query = '''
                    insert into HistorialEstadoInformativoProcesoComercial (
                        id_proceso_comercial,
                        codigo_estado,
                        fecha_registro,
                        observacion,
                        rut_registrado_por
                    )
                    select
                        %(id_proceso_comercial)s,
                        %(codigo_estado)s,
                        %(fecha)s,
                        %(observacion)s,
                        %(rut_registrado_por)s
                    where coalesce(
                        (
                            select codigo_estado
                            from HistorialEstadoInformativoProcesoComercial
                            where id_proceso_comercial = %(id_proceso_comercial)s
                            order by fecha_registro desc
                            limit 1
                        ),
                        ''
                    ) <> %(codigo_estado)s
                '''

                params = {
                    'id_proceso_comercial': historial.id_proceso_comercial,
                    'codigo_estado': historial.codigo_estado,
                    'fecha': historial.fecha,
                    'observacion': historial.observacion,
                    'rut_registrado_por': historial.rut_registrado_por,
                }

                cur.execute(query, params)

                # 2. Actualizar estado actual del proceso comercial

                query = '''
                    update ProcesoComercial
                    set codigo_estado_actual = %(codigo_estado)s
                    where id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial': historial.id_proceso_comercial,
                    'codigo_estado': historial.codigo_estado,
                }

                cur.execute(query, params)