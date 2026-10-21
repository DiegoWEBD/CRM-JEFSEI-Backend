from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioUnidadesAlicuotasPostgres(RepositorioUnidadesAlicuotas):

    def listar_por_oportunidad(self, id_proceso_comercial: int) -> list[UnidadAlicuota]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select identificador_unidad, prorrateo, fila_origen
                    from ProcesoComercialUnidad
                    where id_proceso_comercial = %(id_proceso_comercial)s
                    order by fila_origen, id
                '''

                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    UnidadAlicuota(
                        identificador_unidad=row['identificador_unidad'],
                        prorrateo=row['prorrateo'],
                        fila_origen=row['fila_origen'],
                    )
                    for row in rows
                ]

    def obtener_nombre_excel(self, id_proceso_comercial: int) -> str | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select nombre_excel_alicuota
                    from ProcesoComercial
                    where id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return row['nombre_excel_alicuota'] if row is not None else None

    def guardar_o_reemplazar(
        self,
        id_proceso_comercial: int,
        nombre_excel: str,
        unidades: list[UnidadAlicuota],
    ) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                cur.execute('''
                    delete from ProcesoComercialUnidad
                    where id_proceso_comercial = %(id_proceso_comercial)s
                ''', {'id_proceso_comercial': id_proceso_comercial})

                for unidad in unidades:
                    cur.execute('''
                        insert into ProcesoComercialUnidad
                            (id_proceso_comercial, identificador_unidad, prorrateo, fila_origen)
                        values (%(id_proceso_comercial)s, %(identificador_unidad)s, %(prorrateo)s, %(fila_origen)s)
                    ''', {
                        'id_proceso_comercial': id_proceso_comercial,
                        'identificador_unidad': unidad.identificador_unidad,
                        'prorrateo': unidad.prorrateo,
                        'fila_origen': unidad.fila_origen,
                    })

                cur.execute('''
                    update ProcesoComercial
                    set nombre_excel_alicuota = %(nombre_excel)s
                    where id = %(id_proceso_comercial)s
                ''', {
                    'nombre_excel': nombre_excel,
                    'id_proceso_comercial': id_proceso_comercial,
                })
