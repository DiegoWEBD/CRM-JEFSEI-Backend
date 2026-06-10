from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioSolicitudesCotizacionPostgres(RepositorioSolicitudesCotizacion):

    def obtener_solicitudes_activas(self, id_prospecto: int) -> list[SolicitudCotizacion]:
         with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cotizaciones: list[SolicitudCotizacion] = []

                query = '''
                    select SC.id, SC.tipo
                    from SolicitudCotizacion SC
                    inner join ProcesoComercial PC
                    on SC.id_proceso_comercial = PC.id
                    where not PC.cerrado and PC.id_prospecto = %(id_prospecto)s
                '''

                params = {
                    'id_prospecto': id_prospecto
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                for row in rows:
                    id_solicitud = row['id']
                    tipo = row['tipo']

                    if tipo == 'espacios_comunes':
                        query = '''
                            select prioridad, fecha, observaciones
                            from SolicitudCotizacion
                            where id = %(id_solicitud)s
                        '''

                        params = {
                            'id_solicitud': id_solicitud
                        }

                        cur.execute(query, params)
                        row_solicitud = cur.fetchone()

                        if row_solicitud is None:
                            continue

                        cotizaciones.append(SolicitudCotizacion(
                            id=id_solicitud,
                            tipo=tipo,
                            prioridad=row_solicitud['prioridad'],
                            observaciones=row_solicitud['observaciones'],
                            fecha=row_solicitud['fecha']
                        ))

            return cotizaciones 