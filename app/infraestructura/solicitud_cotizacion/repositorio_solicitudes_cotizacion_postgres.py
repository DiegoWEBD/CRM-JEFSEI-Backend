from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.actividad_accidentes_personales.actividad_accidentes_personales import ActividadAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.solicitud_cotizacion_accidentes_personales import SolicitudCotizacionAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_responsabilidad_civil.solicitud_cotizacion_responsabilidad_civil import SolicitudCotizacionResponsabilidadCivil
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.solicitud_cotizacion_unidades import SolicitudCotizacionUnidades
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_vida_guardia.solicitud_cotizacion_vida_guardia import SolicitudCotizacionVidaGuardia
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioSolicitudesCotizacionPostgres(RepositorioSolicitudesCotizacion):

    def obtener_solicitudes_activas(self, id_prospecto: int) -> list[SolicitudCotizacion]:
         with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cotizaciones: list[SolicitudCotizacion] = []

                query = '''
                    select SC.id, SC.tipo, 
                    PR.nombre as producto,
                    SC.prioridad, SC.fecha,
                    SC.observaciones,
                    SC.recotizacion,
                    P.nombre_riesgo,
                    P.informacion_completa,
                    EJ_COM.nombre as ejecutivo_comercial
                    from SolicitudCotizacion SC
                    inner join ProcesoComercial PC
                    on SC.id_proceso_comercial = PC.id
                    inner join Prospecto P 
                    on PC.id_prospecto = P.id
                    inner join Producto PR
                    on PC.id_producto = PR.id
                    left join Usuario EJ_COM
                    on PC.rut_ej_comercial = EJ_COM.rut
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
                    prioridad = row['prioridad']
                    fecha = row['fecha']
                    observaciones = row['observaciones']
                    recotizacion = row['recotizacion']
                    nombre_riesgo = row['nombre_riesgo']
                    informacion_completa = row['informacion_completa']
                    ejecutivo_comercial = row['ejecutivo_comercial']
                    producto = row['producto']

                    if tipo == 'vida_guardia':
                        query = '''
                            select numero_guardias
                            from SolicitudCotizacionProductoVidaGuardia
                            where id = %(id_solicitud)s
                        '''

                        params = {
                            'id_solicitud': id_solicitud
                        }

                        cur.execute(query, params)
                        row_solicitud = cur.fetchone()

                        if row_solicitud is None:
                            continue

                        cotizaciones.append(SolicitudCotizacionVidaGuardia(
                            id=id_solicitud,
                            tipo=tipo,
                            prioridad=prioridad,
                            observaciones=observaciones,
                            fecha=fecha,
                            recotizacion=recotizacion,
                            nombre_riesgo=nombre_riesgo,
                            informacion_completa=informacion_completa,
                            ejecutivo_comercial=ejecutivo_comercial,
                            producto=producto,
                            numero_guardias=row_solicitud['numero_guardias']
                        ))

                    elif tipo == 'accidentes_personales':
                        query = '''
                            select actividad, numero_asegurados
                            from SolicitudCotizacionProductoAccidentesPersonales
                            where id = %(id_solicitud)s
                        '''

                        params = {
                            'id_solicitud': id_solicitud
                        }

                        cur.execute(query, params)
                        rows_solicitud = cur.fetchall()
                        actividades: list[ActividadAccidentesPersonales] = []

                        for row_solicitud in rows_solicitud:
                            actividades.append(ActividadAccidentesPersonales(
                                actividad=row_solicitud['actividad'],
                                numero_asegurados=row_solicitud['numero_asegurados']
                            ))

                        cotizaciones.append(SolicitudCotizacionAccidentesPersonales(
                            id=id_solicitud,
                            tipo=tipo,
                            prioridad=prioridad,
                            observaciones=observaciones,
                            fecha=fecha,
                            recotizacion=recotizacion,
                            nombre_riesgo=nombre_riesgo,
                            informacion_completa=informacion_completa,
                            ejecutivo_comercial=ejecutivo_comercial,
                            producto=producto,
                            actividades=actividades
                        ))

                    elif tipo == 'unidades':
                        query = '''
                            select monto_asegurado_total, nombre_excel
                            from SolicitudCotizacionProductoUnidades
                            where id = %(id_solicitud)s
                        '''

                        params = {
                            'id_solicitud': id_solicitud
                        }

                        cur.execute(query, params)
                        row_solicitud = cur.fetchone()

                        if row_solicitud is None:
                            continue

                        cotizaciones.append(SolicitudCotizacionUnidades(
                            id=id_solicitud,
                            tipo=tipo,
                            prioridad=prioridad,
                            observaciones=observaciones,
                            fecha=fecha,
                            recotizacion=recotizacion,
                            nombre_riesgo=nombre_riesgo,
                            informacion_completa=informacion_completa,
                            ejecutivo_comercial=ejecutivo_comercial,
                            producto=producto,
                            monto_asegurado_total=row_solicitud['monto_asegurado_total'],
                            nombre_excel=row_solicitud['nombre_excel']
                        ))

                    elif tipo == 'rc_condominio':
                        query = '''
                            select limite_responsabilidad_civil, actividad_del_condominio
                            from SolicitudCotizacionProductoResponsabilidadCivil
                            where id = %(id_solicitud)s
                        '''

                        params = {
                            'id_solicitud': id_solicitud
                        }

                        cur.execute(query, params)
                        row_solicitud = cur.fetchone()

                        if row_solicitud is None:
                            continue

                        cotizaciones.append(SolicitudCotizacionResponsabilidadCivil(
                            id=id_solicitud,
                            tipo=tipo,
                            prioridad=prioridad,
                            observaciones=observaciones,
                            fecha=fecha,
                            recotizacion=recotizacion,
                            nombre_riesgo=nombre_riesgo,
                            informacion_completa=informacion_completa,
                            ejecutivo_comercial=ejecutivo_comercial,
                            producto=producto,
                            limite=row_solicitud['limite_responsabilidad_civil'],
                            actividad_del_condominio=row_solicitud['actividad_del_condominio']
                        ))

                    else:
                        cotizaciones.append(SolicitudCotizacion(
                            id=id_solicitud,
                            tipo=tipo,
                            prioridad=prioridad,
                            observaciones=observaciones,
                            fecha=fecha,
                            recotizacion=recotizacion,
                            nombre_riesgo=nombre_riesgo,
                            informacion_completa=informacion_completa,
                            ejecutivo_comercial=ejecutivo_comercial,
                            producto=producto
                        ))

            return cotizaciones 