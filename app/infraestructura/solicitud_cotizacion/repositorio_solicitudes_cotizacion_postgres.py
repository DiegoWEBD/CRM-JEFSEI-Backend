from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion import SolicitudCotizacion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.actividad_accidentes_personales.actividad_accidentes_personales import ActividadAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_accidentes_personales.solicitud_cotizacion_accidentes_personales import SolicitudCotizacionAccidentesPersonales
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_responsabilidad_civil.solicitud_cotizacion_responsabilidad_civil import SolicitudCotizacionResponsabilidadCivil
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.solicitud_cotizacion_unidades import SolicitudCotizacionUnidades
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_vida_guardia.solicitud_cotizacion_vida_guardia import SolicitudCotizacionVidaGuardia
from app.dominio.usuario.usuario import Usuario
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
                    PC.rut_ej_comercial,
                    EJ_COM.nombre as nombre_ejecutivo_comercial
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
                    rut_ej_comercial = row['rut_ej_comercial']
                    nombre_ejecutivo_comercial = row['nombre_ejecutivo_comercial']
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
                            rut_ejecutivo_comercial=rut_ej_comercial,
                            nombre_ejecutivo_comercial=nombre_ejecutivo_comercial,
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
                            rut_ejecutivo_comercial=rut_ej_comercial,
                            nombre_ejecutivo_comercial=nombre_ejecutivo_comercial,
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
                            rut_ejecutivo_comercial=rut_ej_comercial,
                            nombre_ejecutivo_comercial=nombre_ejecutivo_comercial,
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
                            rut_ejecutivo_comercial=rut_ej_comercial,
                            nombre_ejecutivo_comercial=nombre_ejecutivo_comercial,
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
                            rut_ejecutivo_comercial=rut_ej_comercial,
                            nombre_ejecutivo_comercial=nombre_ejecutivo_comercial,
                            producto=producto
                        ))

            return cotizaciones 
         
    def registrar_nueva_solicitud(self, solicitud: SolicitudCotizacion, id_prospecto: int, registrado_por: Usuario):
        ESTADO_COTIZACION_SOLICITADA = 'COTIZACION_SOLICITADA_COMPANY'
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Búsqueda del producto seleccionado

                query = '''
                    select id
                    from Producto
                    where codigo = %(tipo_solicitud)s
                '''
                
                params = {
                    'tipo_solicitud': solicitud.tipo
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise RecursoNoEncontradoException(f'Producto con código {solicitud.tipo} no encontrado')
                
                id_producto: int = row['id']

                # Creación de nuevo proceso comercial

                query = '''
                    insert into ProcesoComercial (id_prospecto, rut_ej_comercial, rut_ej_evaluacion, id_producto, codigo_estado_actual, renovacion)
                    values (%(id_prospecto)s, %(rut_ej_comercial)s, %(rut_ej_evaluacion)s, %(id_producto)s, %(codigo_estado_actual)s, %(renovacion)s)
                    returning id
                '''
                
                params = {
                    'id_prospecto': id_prospecto,
                    'rut_ej_comercial': solicitud.rut_ejecutivo_comercial,
                    'rut_ej_evaluacion': '15326481-0', # MODIFICAR POST PROYECTO
                    'codigo_estado_actual': ESTADO_COTIZACION_SOLICITADA,
                    'id_producto': id_producto,
                    'renovacion': False
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise Exception('Error al crear un nuevo proceso comercial')
                
                id_proceso_comercial: int = row['id']

                # Creación de solicitud base

                query = '''
                    insert into SolicitudCotizacion (fecha, prioridad, id_proceso_comercial, observaciones, tipo, recotizacion)
                    values (%(fecha)s, %(prioridad)s, %(id_proceso_comercial)s, %(observaciones)s, %(tipo)s, %(recotizacion)s)
                    returning id
                '''
                
                params = {
                    'fecha': solicitud.fecha,
                    'prioridad': solicitud.prioridad,
                    'id_proceso_comercial': id_proceso_comercial,
                    'observaciones': solicitud.observaciones,
                    'tipo': solicitud.tipo,
                    'recotizacion': False
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise Exception('Error al crear nueva solicitud de cotización')
                
                id_solicitud: int = row['id']
                
                # Creación de solicitud específica

                if isinstance(solicitud, SolicitudCotizacionUnidades):
                    query = '''
                        insert into SolicitudCotizacionProductoUnidades (id, monto_asegurado_total, nombre_excel)
                        values (%(id_solicitud)s, %(monto_asegurado_total)s, %(nombre_excel)s)
                    '''
                    
                    params = {
                        'id_solicitud': id_solicitud,
                        'monto_asegurado_total': solicitud.monto_asegurado_total,
                        'nombre_excel': solicitud.nombre_excel
                    }

                    cur.execute(query, params)

                elif isinstance(solicitud, SolicitudCotizacionVidaGuardia):
                    query = '''
                        insert into SolicitudCotizacionProductoVidaGuardia (id, numero_guardias)
                        values (%(id_solicitud)s, %(numero_guardias)s)
                    '''
                    
                    params = {
                        'id_solicitud': id_solicitud,
                        'numero_guardias': solicitud.numero_guardias
                    }

                    cur.execute(query, params)

                elif isinstance(solicitud, SolicitudCotizacionResponsabilidadCivil):
                    query = '''
                        insert into SolicitudCotizacionProductoResponsabilidadCivil (id, limite_responsabilidad_civil, actividad_del_condominio)
                        values (%(id_solicitud)s, %(limite_responsabilidad_civil)s, %(actividad_del_condominio)s)
                    '''
                    
                    params = {
                        'id_solicitud': id_solicitud,
                        'limite_responsabilidad_civil': solicitud.limite,
                        'actividad_del_condominio': solicitud.actividad_del_condominio
                    }

                    cur.execute(query, params)

                elif isinstance(solicitud, SolicitudCotizacionAccidentesPersonales):
                    
                    for actividad_ap in solicitud.actividades:
                        query = '''
                            insert into SolicitudCotizacionProductoAccidentesPersonales (id, actividad, numero_asegurados)
                            values (%(id_solicitud)s, %(actividad)s, %(numero_asegurados)s)
                        '''
                        
                        params = {
                            'id_solicitud': id_solicitud,
                            'actividad': actividad_ap.actividad,
                            'numero_asegurados': actividad_ap.numero_asegurados
                        }

                        cur.execute(query, params)
                    
                # Registro de historial

                query = '''
                    insert into HistorialEstadoInformativoProcesoComercial (id_proceso_comercial, codigo_estado, fecha_registro, rut_registrado_por)
                    values (%(id_proceso_comercial)s, %(codigo_estado)s, %(fecha_registro)s, %(rut_registrado_por)s)
                '''
                
                params = {
                    'id_proceso_comercial': id_proceso_comercial,
                    'codigo_estado': ESTADO_COTIZACION_SOLICITADA,
                    'fecha_registro': solicitud.fecha,
                    'rut_registrado_por': registrado_por.rut
                }

                cur.execute(query, params)
                
    def existe_solicitud(self, id) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Búsqueda del producto seleccionado

                query = '''
                    select id
                    from SolicitudCotizacion
                    where id = %(id)s
                '''
                
                params = {
                    'id': id
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return row is not None