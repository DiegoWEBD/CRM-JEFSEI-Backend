from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.prospecto.adaptadores.tuplerows_prospecto_adapter import TupleRowsProspectoAdapter
from app.infraestructura.prospecto.adaptadores.tuplerows_prospecto_condominio_adapter import TupleRowsProspectoCondominioAdapter


class RepositorioProspectosPostgres(RepositorioProspectos):
    
    def registrar_prospecto_condominio(self, prospecto: ProspectoCondominio) -> int:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Prospecto base
                query = '''
                    insert into Prospecto(
                        rut_riesgo,
                        nombre_riesgo,
                        nombre_contacto,
                        telefono_contacto,
                        correo_contacto,
                        direccion,
                        id_comuna,
                        observaciones,
                        id_linea_negocio,
                        rut_registrado_por
                    )
                    values(
                        %(rut_riesgo)s,
                        %(nombre_riesgo)s,
                        %(nombre_contacto)s,
                        %(telefono_contacto)s,
                        %(correo_contacto)s,
                        %(direccion)s,
                        %(id_comuna)s,
                        %(observaciones)s,
                        %(id_linea_negocio)s,
                        %(rut_registrado_por)s
                    )
                    returning id
                '''

                params = {
                    'rut_riesgo': prospecto.rut_riesgo,
                    'nombre_riesgo': prospecto.nombre_riesgo,
                    'nombre_contacto': prospecto.nombre_contacto,
                    'telefono_contacto': prospecto.telefono_contacto,
                    'correo_contacto': prospecto.correo_contacto,
                    'direccion': prospecto.direccion,
                    'id_comuna': prospecto.comuna.id,
                    'observaciones': prospecto.observaciones,
                    'id_linea_negocio': prospecto.linea_negocio.id,
                    'rut_registrado_por': prospecto.registrado_por.rut,
                }

                cur.execute(query, params)
                id_prospecto: int = cur.fetchone()['id']

                # Prospecto condominio
                query = '''
                    insert into ProspectoCondominio(
                        id,
                        cargo_contacto,
                        tiene_locales_comerciales,
                        uso_del_condominio,
                        numero_pisos,
                        numero_torres,
                        cantidad_departamentos,
                        cantidad_subterraneos,
                        tiene_piscina,
                        year_construccion,
                        metros_cuadrados,
                        desea_ser_contactado
                    )
                    values(
                        %(id)s,
                        %(cargo_contacto)s,
                        %(tiene_locales_comerciales)s,
                        %(uso_del_condominio)s,
                        %(numero_pisos)s,
                        %(numero_torres)s,
                        %(cantidad_departamentos)s,
                        %(cantidad_subterraneos)s,
                        %(tiene_piscina)s,
                        %(year_construccion)s,
                        %(metros_cuadrados)s,
                        %(desea_ser_contactado)s
                    )
                '''

                params = {
                    'id': id_prospecto,
                    'cargo_contacto': prospecto.cargo_contacto,
                    'tiene_locales_comerciales': prospecto.tiene_locales_comerciales,
                    'uso_del_condominio': prospecto.uso_del_condominio,
                    'numero_pisos': prospecto.numero_pisos,
                    'numero_torres': prospecto.numero_torres,
                    'cantidad_departamentos': prospecto.cantidad_departamentos,
                    'cantidad_subterraneos': prospecto.cantidad_subterraneos,
                    'tiene_piscina': prospecto.tiene_piscina,
                    'year_construccion': prospecto.year_construccion,
                    'metros_cuadrados': prospecto.metros_cuadrados,
                    'desea_ser_contactado': prospecto.desea_ser_contactado
                }

                cur.execute(query, params)

                rut_ejecutivo_comercial = prospecto.ejecutivo_comercial_asignado.rut if prospecto.ejecutivo_comercial_asignado else None

                # Proceso comercial
                query = '''
                    insert into ProcesoComercial(id_prospecto, rut_ej_comercial)
                    values (%(id_prospecto)s, %(rut_ej_comercial)s)
                    returning id
                '''           

                params = {
                    'id_prospecto': id_prospecto,
                    'rut_ej_comercial': rut_ejecutivo_comercial
                }     

                cur.execute(query, params)
                id_proceso_comercial: int = cur.fetchone()['id']

                # Estado inicial
                query = '''
                    insert into EstadoParticular(codigo_estado_base)
                    values ('PROSPECTO_CARGADO')
                    returning id
                '''               

                cur.execute(query)
                id_estado_particular: int = cur.fetchone()['id']

                # Registro histórico del estado
                query = '''
                    insert into HistorialEstado(id_proceso_comercial, id_estado_particular_actual, rut_cambiado_por)
                    values(%(id_proceso_comercial)s, %(id_estado_particular_actual)s, %(rut_cambiado_por)s)
                '''           

                params = {
                    'id_proceso_comercial': id_proceso_comercial,
                    'id_estado_particular_actual': id_estado_particular,
                    'rut_cambiado_por': prospecto.registrado_por.rut
                }     

                cur.execute(query, params)

                return id_prospecto

    
    def buscar(self, id: int) -> Prospecto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select LN.nombre as linea_negocio
                    from Prospecto P
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    where P.id = %(id)s
                '''

                params = {
                    'id': id
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return None
                
                linea_negocio = row['linea_negocio']

                if linea_negocio.lower() != 'condominio':
                    return None
                
                query = '''
                    select P.id as id_prospecto,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.nombre_contacto,
                    P.correo_contacto, P.observaciones,
                    LN.nombre as linea_negocio,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    COM.nombre as comuna,
                    SER.id as id_solicitud_evaluacion,
                    SER.fecha_solicitud as fecha_solicitud_evaluacion,
                    SER.prioridad as prioridad_solicitud,
                    ER.id as id_evaluacion,
                    ER.observaciones as observaciones_evaluacion,
                    ER.uf_por_metro_cuadrado as evaluacion_uf_por_metro_cuadrado,
                    ER.porcentaje_depreciacion as evaluacion_porcentaje_depreciacion,
                    ER.porcentaje_espacios_comunes as evaluacion_porcentaje_espacios_comunes,
                    U_EJ_COM.rut as rut_ej_comercial, 
                    U_EJ_COM.nombre as nombre_ej_comercial,
                    U_EJ_EV.rut as rut_ej_evaluacion, 
                    U_EJ_EV.nombre as nombre_ej_evaluacion,
                    EB.nombre as nombre_estado_actual,
                    EB.codigo as codigo_estado_actual,
                    EB.color as color_estado_actual,
                    HE.fecha_registro as fecha_registro_estado,
                    HE.motivo_cambio as motivo_cambio_estado,
                    U_ESTADO.rut as rut_estado_cambiado_por,
                    U_ESTADO.nombre as nombre_estado_cambiado_por,
                    EP.dias_limite_particular, 
                    EB.dias_limite as dias_limite_base,
                    EB_SIG.codigo as codigo_siguiente_estado_esperado,
                    EB_SIG.nombre as nombre_siguiente_estado_esperado,
                    EB_SIG.accion as proxima_accion_esperada,
                    EB2.nombre as nombre_estado_anterior,
                    EB2.codigo as codigo_estado_anterior,
                    extract(day from (now() - HE.fecha_registro)) AS dias_transcurridos
                    from Prospecto P
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    inner join Comuna COM
                    on P.id_comuna = COM.id
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    inner join ProcesoComercial PC
                    on P.id = PC.id_prospecto
                    left join Usuario U_EJ_COM
                    on PC.rut_ej_comercial = U_EJ_COM.rut
                    left join Usuario U_EJ_EV
                    on PC.rut_ej_evaluacion = U_EJ_EV.rut
                    left join SolicitudEvaluacionRiesgo SER
                    on PC.id = SER.id_proceso_comercial
                    left join EvaluacionRiesgo ER
                    on SER.id = ER.id_solicitud
                    left join Cotizacion C
                    on ER.id = C.id_evaluacion
                    left join Poliza PO
                    on C.id = PO.id_cotizacion
                    inner join HistorialEstado HE
                    on PC.id = HE.id_proceso_comercial
                    inner join Usuario U_ESTADO
                    on HE.rut_cambiado_por = U_ESTADO.rut
                    inner join EstadoParticular EP
                    on HE.id_estado_particular_actual = EP.id
                    inner join EstadoBase EB
                    on EP.codigo_estado_base = EB.codigo
                    left join EstadoParticular EP2
                    on HE.id_estado_particular_anterior = EP2.id
                    left join EstadoBase EB2
                    on EP2.codigo_estado_base = EB2.codigo
                    left join EstadoBase EB_SIG
                    on EB.codigo_siguiente_estado = EB_SIG.codigo
                    where P.id = %(id)s
                    order by HE.fecha_registro asc
                '''

                params = {
                    'id': id
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if rows is None or len(rows) == 0:
                    return None

                return TupleRowsProspectoAdapter(rows).to_prospecto()
            
    def buscar_prospecto_condominio(self, id) -> ProspectoCondominio | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select LN.nombre as linea_negocio
                    from Prospecto P
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    where P.id = %(id)s
                '''

                params = {
                    'id': id
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return None
                
                linea_negocio = row['linea_negocio']

                if linea_negocio.lower() != 'condominio':
                    return None
                
                query = '''
                    select P.id as id_prospecto,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.nombre_contacto, PCO.cargo_contacto,
                    P.correo_contacto, P.observaciones,
                    LN.nombre as linea_negocio,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    COM.nombre as comuna,
                    PCO.tiene_locales_comerciales,
                    PCO.uso_del_condominio,
                    PCO.numero_pisos, PCO.numero_torres,
                    PCO.cantidad_departamentos, 
                    PCO.cantidad_subterraneos, PCO.tiene_piscina,
                    PCO.year_construccion, PCO.metros_cuadrados,
                    PCO.desea_ser_contactado,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion,
                    SER.id as id_solicitud_evaluacion,
                    SER.fecha_solicitud as fecha_solicitud_evaluacion,
                    SER.prioridad as prioridad_solicitud,
                    ER.id as id_evaluacion,
                    ER.observaciones as observaciones_evaluacion,
                    ER.uf_por_metro_cuadrado as evaluacion_uf_por_metro_cuadrado,
                    ER.porcentaje_depreciacion as evaluacion_porcentaje_depreciacion,
                    ER.porcentaje_espacios_comunes as evaluacion_porcentaje_espacios_comunes,
                    U_EJ_COM.rut as rut_ej_comercial, 
                    U_EJ_COM.nombre as nombre_ej_comercial,
                    U_EJ_EV.rut as rut_ej_evaluacion, 
                    U_EJ_EV.nombre as nombre_ej_evaluacion,
                    EB.nombre as nombre_estado_actual,
                    EB.codigo as codigo_estado_actual,
                    EB.color as color_estado_actual,
                    HE.fecha_registro as fecha_registro_estado,
                    HE.motivo_cambio as motivo_cambio_estado,
                    U_ESTADO.rut as rut_estado_cambiado_por,
                    U_ESTADO.nombre as nombre_estado_cambiado_por,
                    EP.dias_limite_particular, 
                    EB.dias_limite as dias_limite_base,
                    EB_SIG.codigo as codigo_siguiente_estado_esperado,
                    EB_SIG.nombre as nombre_siguiente_estado_esperado,
                    EB_SIG.accion as proxima_accion_esperada,
                    EB2.nombre as nombre_estado_anterior,
                    EB2.codigo as codigo_estado_anterior,
                    extract(day from (now() - HE.fecha_registro)) AS dias_transcurridos
                    from Prospecto P
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    inner join Comuna COM
                    on P.id_comuna = COM.id
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    inner join ProcesoComercial PC
                    on P.id = PC.id_prospecto
                    left join Usuario U_EJ_COM
                    on PC.rut_ej_comercial = U_EJ_COM.rut
                    left join Usuario U_EJ_EV
                    on PC.rut_ej_evaluacion = U_EJ_EV.rut
                    left join SolicitudEvaluacionRiesgo SER
                    on PC.id = SER.id_proceso_comercial
                    left join EvaluacionRiesgo ER
                    on SER.id = ER.id_solicitud
                    left join Cotizacion C
                    on ER.id = C.id_evaluacion
                    left join Poliza PO
                    on C.id = PO.id_cotizacion
                    left join PlanificacionProspecto PP
                    on P.id = PP.id_prospecto
                    left join CompanySeguros CS_PLAN
                    on PP.id_company = CS_PLAN.id
                    inner join HistorialEstado HE
                    on PC.id = HE.id_proceso_comercial
                    inner join Usuario U_ESTADO
                    on HE.rut_cambiado_por = U_ESTADO.rut
                    inner join EstadoParticular EP
                    on HE.id_estado_particular_actual = EP.id
                    inner join EstadoBase EB
                    on EP.codigo_estado_base = EB.codigo
                    left join EstadoParticular EP2
                    on HE.id_estado_particular_anterior = EP2.id
                    left join EstadoBase EB2
                    on EP2.codigo_estado_base = EB2.codigo
                    left join EstadoBase EB_SIG
                    on EB.codigo_siguiente_estado = EB_SIG.codigo
                    inner join ProspectoCondominio PCO
                    on P.id = PCO.id
                    where P.id = %(id)s
                    order by HE.fecha_registro asc
                '''

                params = {
                    'id': id
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if rows is None or len(rows) == 0:
                    return None

                print(len(rows))
                return TupleRowsProspectoCondominioAdapter(rows).to_prospecto_condominio()
                
    def asignar_ejecutivo_comercial(self, prospecto: Prospecto, asignado_por: Usuario) -> None:
        if not prospecto.id or not prospecto.ejecutivo_comercial_asignado:
            return
        
        CODIGO_EJECUTIVO_ASIGNADO = 'EJECUTIVO_COMERCIAL_ASIGNADO'
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                print('asignando')

                query = '''
                    update ProcesoComercial
                    set rut_ej_comercial = %(rut_ej_comercial)s
                    where id_prospecto = %(id_prospecto)s
                    returning id
                '''
                params = {
                    'rut_ej_comercial': prospecto.ejecutivo_comercial_asignado.rut,
                    'id_prospecto': prospecto.id
                }

                cur.execute(query, params)
                id_proceso_comercial: int = cur.fetchone()['id']

                # Registro de cambio de estado
                query = '''
                    select id_estado_particular_actual
                    from HistorialEstado
                    where id_proceso_comercial = %(id_proceso_comercial)s
                    order by fecha_registro desc
                    limit 1
                '''
                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                id_estado_particular_actual: int = cur.fetchone()['id_estado_particular_actual']

                query = '''
                    insert into EstadoParticular(codigo_estado_base)
                    values (%(codigo_estado_base)s)
                    returning id
                '''
                params = {
                    'codigo_estado_base': CODIGO_EJECUTIVO_ASIGNADO
                }

                cur.execute(query, params)
                id_estado_particular_nuevo: int = cur.fetchone()['id']

                query = '''
                    insert into HistorialEstado(
                        id_proceso_comercial, 
                        id_estado_particular_anterior,
                        id_estado_particular_actual,
                        rut_cambiado_por
                    )
                    values (
                        %(id_proceso_comercial)s,
                        %(id_estado_particular_anterior)s,
                        %(id_estado_particular_actual)s,
                        %(rut_cambiado_por)s
                    )
                '''
                params = {
                    'id_proceso_comercial': id_proceso_comercial,
                    'id_estado_particular_anterior': id_estado_particular_actual,
                    'id_estado_particular_actual': id_estado_particular_nuevo,
                    'rut_cambiado_por': asignado_por.rut
                }

                cur.execute(query, params)


    def asignar_ejecutivo_evaluacion_proyectos(self, prospecto: Prospecto) -> None:
        if prospecto.id is None or prospecto.evaluacion_riesgo is None or prospecto.evaluacion_riesgo.ej_evaluacion is None:
            return
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select id
                    from ProcesoComercial
                    where id_prospecto = %(id_prospecto)s
                '''
                params = {
                    'id_prospecto': prospecto.id
                }

                cur.execute(query, params)
                id_proceso_comercial: int = cur.fetchone()['id']

                query = '''
                    update EvaluacionRiesgo
                    set rut_ej_evaluacion = %(rut_ej_evaluacion)s
                    where id_proceso_comercial = %(id_proceso_comercial)s
                '''
                params = {
                    'rut_ej_evaluacion': prospecto.evaluacion_riesgo.ej_evaluacion.rut,
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)

    def cambiar_siguiente_estado(self, id: int) -> None:
        pass
