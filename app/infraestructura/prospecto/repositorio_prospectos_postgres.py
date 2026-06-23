from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.prospecto.adaptadores.dictrow_prospecto_adapter import DictRowProspectoAdapter
from app.infraestructura.prospecto.adaptadores.dictrow_prospecto_condominio_adapter import DictRowProspectoCondominioAdapter
from app.presentacion.api.prospecto.lib.informacion_completa_prospecto import informacion_completa_prospecto_condominio


class RepositorioProspectosPostgres(RepositorioProspectos):
    
    def registrar_prospecto_condominio(self, prospecto: ProspectoCondominio) -> int:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Prospecto base
                query = '''
                    insert into Prospecto(
                        rut_riesgo,
                        nombre_riesgo,
                        telefono_contacto,
                        correo_contacto,
                        direccion,
                        region,
                        comuna,
                        observaciones,
                        id_linea_negocio,
                        rut_registrado_por,
                        rut_ej_comercial_asignado,
                        informacion_completa
                    )
                    values(
                        %(rut_riesgo)s,
                        %(nombre_riesgo)s,
                        %(telefono_contacto)s,
                        %(correo_contacto)s,
                        %(direccion)s,
                        %(region)s,
                        %(comuna)s,
                        %(observaciones)s,
                        %(id_linea_negocio)s,
                        %(rut_registrado_por)s,
                        %(rut_ej_comercial_asignado)s,
                        %(informacion_completa)s
                    )
                    returning id
                '''

                params = {
                    'rut_riesgo': prospecto.rut_riesgo,
                    'nombre_riesgo': prospecto.nombre_riesgo,
                    'telefono_contacto': prospecto.telefono_contacto,
                    'correo_contacto': prospecto.correo_contacto,
                    'direccion': prospecto.direccion,
                    'region': prospecto.region,
                    'comuna': prospecto.comuna,
                    'observaciones': prospecto.observaciones,
                    'id_linea_negocio': prospecto.linea_negocio.id,
                    'rut_registrado_por': prospecto.registrado_por.rut,
                    'rut_ej_comercial_asignado': prospecto.ejecutivo_comercial_asignado.rut if prospecto.ejecutivo_comercial_asignado else None,
                    'informacion_completa': informacion_completa_prospecto_condominio(prospecto)
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise ValueError('Error al registrar prospecto')

                id_prospecto: int = row['id']

                # Prospecto condominio
                query = '''
                    insert into ProspectoCondominio(
                        id,
                        id_administrador,
                        tiene_locales_comerciales,
                        uso_del_condominio,
                        materialidad,
                        clasificacion_preliminar_incendio,
                        procesos_productivos,
                        numero_pisos,
                        numero_torres,
                        cantidad_departamentos,
                        cantidad_subterraneos,
                        tiene_piscina,
                        ubicacion_piscina,
                        tiene_alarma_incendio,
                        tiene_sprinklers,
                        year_construccion,
                        metros_cuadrados,
                        uf_por_metro_cuadrado,
                        porcentaje_depreciacion,
                        porcentaje_espacios_comunes
                    )
                    values(
                        %(id)s,
                        %(id_administrador)s,
                        %(tiene_locales_comerciales)s,
                        %(uso_del_condominio)s,
                        %(materialidad)s,
                        %(clasificacion_preliminar_incendio)s,
                        %(procesos_productivos)s,
                        %(numero_pisos)s,
                        %(numero_torres)s,
                        %(cantidad_departamentos)s,
                        %(cantidad_subterraneos)s,
                        %(tiene_piscina)s,
                        %(ubicacion_piscina)s,
                        %(tiene_alarma_incendio)s,
                        %(tiene_sprinklers)s,
                        %(year_construccion)s,
                        %(metros_cuadrados)s,
                        %(uf_por_metro_cuadrado)s,
                        %(porcentaje_depreciacion)s,
                        %(porcentaje_espacios_comunes)s
                    )
                '''

                params = {
                    'id': id_prospecto,
                    'id_administrador': prospecto.administrador.id if prospecto.administrador else None,
                    'tiene_locales_comerciales': prospecto.tiene_locales_comerciales,
                    'uso_del_condominio': prospecto.uso_del_condominio,
                    'materialidad': prospecto.materialidad,
                    'clasificacion_preliminar_incendio': prospecto.clasificacion_preliminar_incendio,
                    'procesos_productivos': prospecto.procesos_productivos,
                    'numero_pisos': prospecto.numero_pisos,
                    'numero_torres': prospecto.numero_torres,
                    'cantidad_departamentos': prospecto.cantidad_departamentos,
                    'cantidad_subterraneos': prospecto.cantidad_subterraneos,
                    'tiene_piscina': prospecto.tiene_piscina,
                    'ubicacion_piscina': prospecto.ubicacion_piscina,
                    'tiene_alarma_incendio': prospecto.tiene_alarma_incendio,
                    'tiene_sprinklers': prospecto.tiene_sprinklers,
                    'year_construccion': prospecto.year_construccion,
                    'metros_cuadrados': prospecto.metros_cuadrados,
                    'uf_por_metro_cuadrado': prospecto.uf_por_metro_cuadrado,
                    'porcentaje_depreciacion': prospecto.porcentaje_depreciacion,
                    'porcentaje_espacios_comunes': prospecto.porcentaje_espacios_comunes,
                }

                cur.execute(query, params)

                return id_prospecto

    def actualizar_prospecto_condominio(self, prospecto: ProspectoCondominio) -> None:
        if prospecto.id is None:
            return
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Datos básicos del prospecto
                query = '''
                    update Prospecto
                    set rut_riesgo = %(rut_riesgo)s,
                    nombre_riesgo = %(nombre_riesgo)s,
                    telefono_contacto = %(telefono_contacto)s,
                    correo_contacto = %(correo_contacto)s,
                    direccion = %(direccion)s,
                    region = %(region)s,
                    comuna = %(comuna)s,
                    observaciones = %(observaciones)s,
                    id_linea_negocio = %(id_linea_negocio)s,
                    informacion_completa = %(informacion_completa)s
                    where id = %(id)s
                '''

                params = {
                    'rut_riesgo': prospecto.rut_riesgo,
                    'nombre_riesgo': prospecto.nombre_riesgo,
                    'telefono_contacto': prospecto.telefono_contacto,
                    'correo_contacto': prospecto.correo_contacto,
                    'direccion': prospecto.direccion,
                    'region': prospecto.region,
                    'comuna': prospecto.comuna,
                    'observaciones': prospecto.observaciones,
                    'id_linea_negocio': prospecto.linea_negocio.id,
                    'informacion_completa': informacion_completa_prospecto_condominio(prospecto),
                    'id': prospecto.id
                }

                cur.execute(query, params)

                # Datos específicos del condominio
                query = '''
                    update ProspectoCondominio
                    set tiene_locales_comerciales = %(tiene_locales_comerciales)s,
                    uso_del_condominio = %(uso_del_condominio)s,
                    materialidad = %(materialidad)s,
                    clasificacion_preliminar_incendio = %(clasificacion_preliminar_incendio)s,
                    procesos_productivos = %(procesos_productivos)s,
                    numero_pisos = %(numero_pisos)s,
                    numero_torres = %(numero_torres)s,
                    cantidad_departamentos = %(cantidad_departamentos)s,
                    cantidad_subterraneos = %(cantidad_subterraneos)s,
                    tiene_piscina = %(tiene_piscina)s,
                    ubicacion_piscina = %(ubicacion_piscina)s,
                    tiene_alarma_incendio = %(tiene_alarma_incendio)s,
                    tiene_sprinklers = %(tiene_sprinklers)s,
                    year_construccion = %(year_construccion)s,
                    metros_cuadrados = %(metros_cuadrados)s,
                    uf_por_metro_cuadrado = %(uf_por_metro_cuadrado)s,
                    porcentaje_depreciacion = %(porcentaje_depreciacion)s,
                    porcentaje_espacios_comunes = %(porcentaje_espacios_comunes)s
                    where id = %(id)s
                '''

                params = {
                    'tiene_locales_comerciales': prospecto.tiene_locales_comerciales,
                    'uso_del_condominio': prospecto.uso_del_condominio,
                    'materialidad': prospecto.materialidad,
                    'clasificacion_preliminar_incendio': prospecto.clasificacion_preliminar_incendio,
                    'procesos_productivos': prospecto.procesos_productivos,
                    'numero_pisos': prospecto.numero_pisos,
                    'numero_torres': prospecto.numero_torres,
                    'cantidad_departamentos': prospecto.cantidad_departamentos,
                    'cantidad_subterraneos': prospecto.cantidad_subterraneos,
                    'tiene_piscina': prospecto.tiene_piscina,
                    'ubicacion_piscina': prospecto.ubicacion_piscina,
                    'tiene_alarma_incendio': prospecto.tiene_alarma_incendio,
                    'tiene_sprinklers': prospecto.tiene_sprinklers,
                    'year_construccion': prospecto.year_construccion,
                    'metros_cuadrados': prospecto.metros_cuadrados,
                    'uf_por_metro_cuadrado': prospecto.uf_por_metro_cuadrado,
                    'porcentaje_depreciacion': prospecto.porcentaje_depreciacion,
                    'porcentaje_espacios_comunes': prospecto.porcentaje_espacios_comunes,
                    'id': prospecto.id
                }

                cur.execute(query, params)


    def buscar(self, id: int) -> Prospecto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select P.id as id_prospecto,
                    CL.id as id_cliente,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    P.rut_ej_comercial_asignado, EJ_COM.nombre as nombre_ej_comercial_asignado,
                    P.region, P.comuna,
                    P.correo_contacto, P.observaciones,
                    P.updated_at as prospecto_updated_at,
                    P.informacion_completa,
                    LN.id as id_linea_negocio,
                    LN.nombre as linea_negocio,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion
                    from Prospecto P
                    left join Cliente CL
                    on P.id = CL.id_prospecto
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    left join Usuario EJ_COM
                    on P.rut_ej_comercial_asignado = EJ_COM.rut
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    left join PlanificacionProspecto PP
                    on P.id = PP.id_prospecto
                    left join CompanySeguros CS_PLAN
                    on PP.id_company = CS_PLAN.id
                    where P.id = %(id)s
                '''

                params = {
                    'id': id
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowProspectoAdapter(row).to_prospecto() if row else None
            
            
    def buscar_prospecto_condominio(self, id: int) -> ProspectoCondominio | None:
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
                    CL.id as id_cliente,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    P.rut_ej_comercial_asignado, EJ_COM.nombre as nombre_ej_comercial_asignado,
                    P.region, P.comuna,
                    P.correo_contacto, P.observaciones,
                    P.informacion_completa,
                    P.updated_at as prospecto_updated_at,
                    PCO.updated_at as condominio_updated_at,
                    LN.id as id_linea_negocio,
                    LN.nombre as linea_negocio,
                    PCO.id_administrador,
                    AC.nombre_administrador,
                    AC.nombre_contacto,
                    AC.telefono as telefono_administrador,
                    AC.correo as correo_administrador,
                    PCO.tiene_locales_comerciales,
                    PCO.uso_del_condominio,
                    PCO.materialidad,
                    PCO.clasificacion_preliminar_incendio,
                    PCO.procesos_productivos,
                    PCO.numero_pisos, PCO.numero_torres,
                    PCO.cantidad_departamentos, 
                    PCO.cantidad_subterraneos, PCO.tiene_piscina,
                    PCO.ubicacion_piscina,
                    PCO.tiene_alarma_incendio,
                    PCO.tiene_sprinklers,
                    PCO.year_construccion, PCO.metros_cuadrados,
                    PCO.uf_por_metro_cuadrado,
                    PCO.porcentaje_depreciacion,
                    PCO.porcentaje_espacios_comunes,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion
                    from Prospecto P
                    inner join ProspectoCondominio PCO
                    on P.id = PCO.id
                    left join Cliente CL
                    on P.id = CL.id_prospecto
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    left join Usuario EJ_COM
                    on P.rut_ej_comercial_asignado = EJ_COM.rut
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    left join AdministradorCondominio AC
                    on PCO.id_administrador = AC.id
                    left join PlanificacionProspecto PP
                    on P.id = PP.id_prospecto
                    left join CompanySeguros CS_PLAN
                    on PP.id_company = CS_PLAN.id
                    where P.id = %(id)s
                '''

                params = {
                    'id': id
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowProspectoCondominioAdapter(row).to_prospecto_condominio() if row else None
                
    def asignar_ejecutivo_comercial(self, prospecto: Prospecto, asignado_por: Usuario) -> None:
        if not prospecto.id or not prospecto.proceso_comercial or not prospecto.proceso_comercial.ejecutivo_comercial:
            return
        
        CODIGO_EJECUTIVO = 'EJECUTIVO_COMERCIAL'
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update ProcesoComercial
                    set rut_ej_comercial = %(rut_ej_comercial)s
                    where id_prospecto = %(id_prospecto)s
                    returning id
                '''
                params = {
                    'rut_ej_comercial': prospecto.proceso_comercial.ejecutivo_comercial.rut,
                    'id_prospecto': prospecto.id
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise ValueError('Error al asignar ejecutivo comercial al prospecto')

                id_proceso_comercial: int = row['id']

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
                row = cur.fetchone()

                if row is None:
                    raise ValueError('Error al asignar ejecutivo comercial al prospecto')

                id_estado_particular_actual: int = row['id_estado_particular_actual']

                query = '''
                    insert into EstadoParticular(codigo_estado_base)
                    values (%(codigo_estado_base)s)
                    returning id
                '''
                params = {
                    'codigo_estado_base': CODIGO_EJECUTIVO
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise ValueError('Error al asignar ejecutivo comercial al prospecto')

                id_estado_particular_nuevo: int = row['id']

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


    # ARREGLAR LUEGO
    def asignar_ejecutivo_evaluacion_proyectos(self, prospecto: Prospecto, asignado_por: Usuario) -> None:
        if not prospecto.id or not prospecto.proceso_comercial or not prospecto.proceso_comercial.ejecutivo_comercial:
            return
        
        CODIGO_EJECUTIVO = 'EJECUTIVO_COMERCIAL'
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update ProcesoComercial
                    set rut_ej_comercial = %(rut_ej_comercial)s
                    where id_prospecto = %(id_prospecto)s
                    returning id
                '''
                params = {
                    'rut_ej_comercial': prospecto.ejecutivo_comercial.rut,
                    'id_prospecto': prospecto.id
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise ValueError('Error al registrar prospecto')

                id_proceso_comercial: int = row['id']

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
                row = cur.fetchone()

                if row is None:
                    raise ValueError('Error al registrar prospecto')

                id_estado_particular_actual: int = row['id_estado_particular_actual']

                query = '''
                    insert into EstadoParticular(codigo_estado_base)
                    values (%(codigo_estado_base)s)
                    returning id
                '''
                params = {
                    'codigo_estado_base': CODIGO_EJECUTIVO
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise ValueError('Error al registrar prospecto')

                id_estado_particular_nuevo: int = row['id']

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

    def cambiar_siguiente_estado(self, id: int) -> None:
        pass
