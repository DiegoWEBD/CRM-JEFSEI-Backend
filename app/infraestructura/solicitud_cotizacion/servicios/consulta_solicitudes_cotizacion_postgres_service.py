from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import SolicitudCotizacionResumen
from app.aplicacion.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_service import ConsultaSolicitudesCotizacionService
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.solicitud_cotizacion.adaptadores.dictrow_solicitud_cotizacion_resumen_adapter import DictRowSolicitudCotizacionResumenAdapter


class ConsultaSolicitudesCotizacionPostgresService(ConsultaSolicitudesCotizacionService):

    def obtener_todas(self, rut_usuario: str | None) -> list[SolicitudCotizacionResumen]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select SC.id,
                    P.nombre_riesgo,
                    PC.id_prospecto,
                    P.informacion_completa,
                    EJ_COM.nombre as ejecutivo_comercial,
                    SC.tipo,
                    SC.recotizacion,
                    SC.motivo_recotizacion,
                    PR.nombre as producto, 
                    SC.prioridad, SC.fecha,
                    count(C.id) as cantidad_cotizaciones
                    from SolicitudCotizacion SC
                    left join Cotizacion C
                    on SC.id = C.id_solicitud
                    inner join ProcesoComercial PC
                    on SC.id_proceso_comercial = PC.id
                    inner join Producto PR
                    on PC.id_producto = PR.id
                    inner join Usuario EJ_COM
                    on PC.rut_ej_comercial = EJ_COM.rut
                    inner join Prospecto P
                    on PC.id_prospecto = P.id
                    where not PC.cerrado 
                    and (
                        cast(%(rut_usuario)s as varchar) is null
                        or P.rut_ej_comercial_asignado = %(rut_usuario)s
                        or P.rut_ej_evaluacion_asignado = %(rut_usuario)s
                    )
                    group by
                        SC.id,
                        P.nombre_riesgo,
                        PC.id_prospecto,
                        P.informacion_completa,
                        EJ_COM.nombre,
                        PR.nombre,
                        SC.prioridad,
                        SC.fecha
                    order by SC.fecha desc
                '''

                params = {
                    'rut_usuario': rut_usuario
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowSolicitudCotizacionResumenAdapter(row).to_solicitud_cotizacion_resumen() for row in rows]