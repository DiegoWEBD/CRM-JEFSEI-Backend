from app.dominio.solicitud_cotizacion.repositorio_unidades_alicuotas import RepositorioUnidadesAlicuotas
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioUnidadesAlicuotasPostgres(RepositorioUnidadesAlicuotas):

    def listar_por_solicitud(self, id_solicitud: int) -> list[UnidadAlicuota]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select identificador_unidad, prorrateo, fila_origen
                    from SolicitudCotizacionUnidad
                    where id_solicitud = %(id_solicitud)s
                    order by fila_origen, id
                '''

                params = {
                    'id_solicitud': id_solicitud
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
