from app.dominio.configuracion_condominio.servicio_calculo_depreciacion import ServicioCalculoDepreciacion
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.linea_negocio.linea_negocio import CODIGO_LINEA_CONDOMINIOS, CODIGO_LINEAS_COMERCIALES
from app.dominio.prospecto.prospecto import Prospecto
from app.dominio.prospecto.prospecto_condominio.prospecto_condominio import ProspectoCondominio
from app.dominio.prospecto.prospecto_empresa.giro_comercial import GiroComercial
from app.dominio.prospecto.prospecto_empresa.prospecto_empresa import ProspectoEmpresa
from app.dominio.prospecto.prospecto_empresa.servicio_giros_comerciales import ServicioGirosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.usuario import Usuario
from app.infraestructura.configuracion_condominio.repositorio_configuracion_condominio_postgres import RepositorioConfiguracionCondominioPostgres
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.lib.normalizar_texto import normalizar_texto
from app.infraestructura.prospecto.adaptadores.dictrow_prospecto_adapter import DictRowProspectoAdapter
from app.infraestructura.prospecto.adaptadores.dictrow_prospecto_condominio_adapter import DictRowProspectoCondominioAdapter
from app.infraestructura.prospecto.adaptadores.dictrow_prospecto_empresa_adapter import DictRowProspectoEmpresaAdapter
from app.presentacion.api.prospecto.lib.informacion_completa_prospecto import informacion_completa_prospecto, informacion_completa_prospecto_condominio, informacion_completa_prospecto_empresa


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
                        porcentaje_espacios_comunes,
                        condominio_vertical
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
                        %(porcentaje_espacios_comunes)s,
                        %(condominio_vertical)s
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
                    'porcentaje_espacios_comunes': prospecto.porcentaje_espacios_comunes,
                    'condominio_vertical': prospecto.condominio_vertical,
                }

                cur.execute(query, params)

                return id_prospecto

    def registrar_prospecto(self, prospecto: Prospecto) -> int:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

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
                    'informacion_completa': informacion_completa_prospecto(prospecto)
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise ValueError('Error al registrar prospecto')

                return row['id']

    def actualizar_prospecto(self, prospecto: Prospecto) -> None:
        if prospecto.id is None:
            return

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

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
                    informacion_completa = %(informacion_completa)s,
                    id_linea_negocio = %(id_linea_negocio)s,
                    rut_ej_comercial_asignado = %(rut_ej_comercial_asignado)s,
                    rut_ej_evaluacion_asignado = %(rut_ej_evaluacion_asignado)s
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
                    'informacion_completa': informacion_completa_prospecto(prospecto),
                    'id': prospecto.id,
                    'id_linea_negocio': prospecto.linea_negocio.id,
                    'rut_ej_comercial_asignado': prospecto.ejecutivo_comercial_asignado.rut if prospecto.ejecutivo_comercial_asignado else None,
                    'rut_ej_evaluacion_asignado': prospecto.ejecutivo_evaluacion_asignado.rut if prospecto.ejecutivo_evaluacion_asignado else None,
                }

                cur.execute(query, params)

                # Actualización de ejecutivos en cliente
                query = '''
                    update Cliente
                    set rut_ej_cobranza_asignado = %(rut_ej_cobranza_asignado)s,
                    rut_ej_renovacion_asignado = %(rut_ej_renovacion_asignado)s,
                    rut_as_renovacion_asignado = %(rut_as_renovacion_asignado)s
                    where id_prospecto = %(id_prospecto)s
                '''

                params = {
                    'rut_ej_cobranza_asignado': prospecto.ejecutivo_cobranza_asignado.rut if prospecto.ejecutivo_cobranza_asignado else None,
                    'rut_ej_renovacion_asignado': prospecto.ejecutivo_renovacion_asignado.rut if prospecto.ejecutivo_renovacion_asignado else None,
                    'rut_as_renovacion_asignado': prospecto.asistente_renovacion_asignado.rut if prospecto.asistente_renovacion_asignado else None,
                    'id_prospecto': prospecto.id
                }

                cur.execute(query, params)

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
                    porcentaje_espacios_comunes = %(porcentaje_espacios_comunes)s,
                    valor_uf_m2_personalizado = %(valor_uf_m2_personalizado)s,
                    porcentaje_depreciacion_personalizado = %(porcentaje_depreciacion_personalizado)s,
                    condominio_vertical = %(condominio_vertical)s,
                    id_administrador = %(id_administrador)s
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
                    'porcentaje_espacios_comunes': prospecto.porcentaje_espacios_comunes,
                    'valor_uf_m2_personalizado': prospecto.valor_uf_m2_personalizado,
                    'porcentaje_depreciacion_personalizado': prospecto.porcentaje_depreciacion_personalizado,
                    'condominio_vertical': prospecto.condominio_vertical,
                    'id_administrador': prospecto.administrador.id if prospecto.administrador else None,
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
                    P.rut_ej_evaluacion_asignado, EJ_EV.nombre as nombre_ej_evaluacion_asignado,
                    CL.rut_ej_cobranza_asignado, EJ_CB.nombre as nombre_ej_cobranza_asignado,
                    CL.rut_ej_renovacion_asignado, EJ_RN.nombre as nombre_ej_renovacion_asignado,
                    CL.rut_as_renovacion_asignado, AS_RN.nombre as nombre_as_renovacion_asignado,
                    P.region, P.comuna,
                    P.correo_contacto, P.observaciones,
                    P.updated_at as prospecto_updated_at,
                    P.informacion_completa,
                    LN.id as id_linea_negocio,
                    LN.nombre as linea_negocio,
                    LN.codigo as codigo_linea_negocio,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion,
                    CASE
                        WHEN CL.id IS NULL THEN 'prospecto'
                        WHEN EXISTS (
                            SELECT 1 FROM Poliza PZ
                            WHERE PZ.id_cliente = CL.id
                              AND PZ.cancelada = false
                              AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                        ) THEN 'cliente_activo'
                        ELSE 'cliente_inactivo'
                    END as estado_general_cliente
                    from Prospecto P
                    left join Cliente CL
                    on P.id = CL.id_prospecto
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    left join Usuario EJ_COM
                    on P.rut_ej_comercial_asignado = EJ_COM.rut
                    left join Usuario EJ_EV
                    on P.rut_ej_evaluacion_asignado = EJ_EV.rut
                    left join Usuario EJ_CB
                    on CL.rut_ej_cobranza_asignado = EJ_CB.rut
                    left join Usuario EJ_RN
                    on CL.rut_ej_renovacion_asignado = EJ_RN.rut
                    left join Usuario AS_RN
                    on CL.rut_as_renovacion_asignado = AS_RN.rut
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

    def buscar_prospecto_por_nombre(self, nombre: str) -> Prospecto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select P.id as id_prospecto,
                    CL.id as id_cliente,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    P.rut_ej_comercial_asignado, EJ_COM.nombre as nombre_ej_comercial_asignado,
                    P.rut_ej_evaluacion_asignado, EJ_EV.nombre as nombre_ej_evaluacion_asignado,
                    CL.rut_ej_cobranza_asignado, EJ_CB.nombre as nombre_ej_cobranza_asignado,
                    CL.rut_ej_renovacion_asignado, EJ_RN.nombre as nombre_ej_renovacion_asignado,
                    CL.rut_as_renovacion_asignado, AS_RN.nombre as nombre_as_renovacion_asignado,
                    P.region, P.comuna,
                    P.correo_contacto, P.observaciones,
                    P.updated_at as prospecto_updated_at,
                    P.informacion_completa,
                    LN.id as id_linea_negocio,
                    LN.nombre as linea_negocio,
                    LN.codigo as codigo_linea_negocio,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion,
                    CASE
                        WHEN CL.id IS NULL THEN 'prospecto'
                        WHEN EXISTS (
                            SELECT 1 FROM Poliza PZ
                            WHERE PZ.id_cliente = CL.id
                                AND PZ.cancelada = false
                                AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                        ) THEN 'cliente_activo'
                        ELSE 'cliente_inactivo'
                    END as estado_general_cliente
                    from Prospecto P
                    left join Cliente CL
                    on P.id = CL.id_prospecto
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    left join Usuario EJ_COM
                    on P.rut_ej_comercial_asignado = EJ_COM.rut
                    left join Usuario EJ_EV
                    on P.rut_ej_evaluacion_asignado = EJ_EV.rut
                    left join Usuario EJ_CB
                    on CL.rut_ej_cobranza_asignado = EJ_CB.rut
                    left join Usuario EJ_RN
                    on CL.rut_ej_renovacion_asignado = EJ_RN.rut
                    left join Usuario AS_RN
                    on CL.rut_as_renovacion_asignado = AS_RN.rut
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    left join PlanificacionProspecto PP
                    on P.id = PP.id_prospecto
                    left join CompanySeguros CS_PLAN
                    on PP.id_company = CS_PLAN.id
                    where unaccent(lower(P.nombre_riesgo)) = unaccent(lower(%(nombre_riesgo)s))
                '''

                params = {
                    'nombre_riesgo': nombre
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowProspectoAdapter(row).to_prospecto() if row else None


    def buscar_prospecto_por_rut(self, rut: str) -> Prospecto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select P.id as id_prospecto,
                    CL.id as id_cliente,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    P.rut_ej_comercial_asignado, EJ_COM.nombre as nombre_ej_comercial_asignado,
                    P.rut_ej_evaluacion_asignado, EJ_EV.nombre as nombre_ej_evaluacion_asignado,
                    CL.rut_ej_cobranza_asignado, EJ_CB.nombre as nombre_ej_cobranza_asignado,
                    CL.rut_ej_renovacion_asignado, EJ_RN.nombre as nombre_ej_renovacion_asignado,
                    CL.rut_as_renovacion_asignado, AS_RN.nombre as nombre_as_renovacion_asignado,
                    P.region, P.comuna,
                    P.correo_contacto, P.observaciones,
                    P.updated_at as prospecto_updated_at,
                    P.informacion_completa,
                    LN.id as id_linea_negocio,
                    LN.nombre as linea_negocio,
                    LN.codigo as codigo_linea_negocio,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion,
                    CASE
                        WHEN CL.id IS NULL THEN 'prospecto'
                        WHEN EXISTS (
                            SELECT 1 FROM Poliza PZ
                            WHERE PZ.id_cliente = CL.id
                                AND PZ.cancelada = false
                                AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                        ) THEN 'cliente_activo'
                        ELSE 'cliente_inactivo'
                    END as estado_general_cliente
                    from Prospecto P
                    left join Cliente CL
                    on P.id = CL.id_prospecto
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    left join Usuario EJ_COM
                    on P.rut_ej_comercial_asignado = EJ_COM.rut
                    left join Usuario EJ_EV
                    on P.rut_ej_evaluacion_asignado = EJ_EV.rut
                    left join Usuario EJ_CB
                    on CL.rut_ej_cobranza_asignado = EJ_CB.rut
                    left join Usuario EJ_RN
                    on CL.rut_ej_renovacion_asignado = EJ_RN.rut
                    left join Usuario AS_RN
                    on CL.rut_as_renovacion_asignado = AS_RN.rut
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    left join PlanificacionProspecto PP
                    on P.id = PP.id_prospecto
                    left join CompanySeguros CS_PLAN
                    on PP.id_company = CS_PLAN.id
                    where replace(replace(P.rut_riesgo, '.', ''), '-', '') =
                          replace(replace(%(rut_riesgo)s, '.', ''), '-', '')
                '''

                params = {
                    'rut_riesgo': rut
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowProspectoAdapter(row).to_prospecto() if row else None


    def buscar_prospecto_por_proceso_comercial(self, id_proceso: int) -> Prospecto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select P.id as id_prospecto,
                    CL.id as id_cliente,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    P.rut_ej_comercial_asignado, EJ_COM.nombre as nombre_ej_comercial_asignado,
                    P.rut_ej_evaluacion_asignado, EJ_EV.nombre as nombre_ej_evaluacion_asignado,
                    CL.rut_ej_cobranza_asignado, EJ_CB.nombre as nombre_ej_cobranza_asignado,
                    CL.rut_ej_renovacion_asignado, EJ_RN.nombre as nombre_ej_renovacion_asignado,
                    CL.rut_as_renovacion_asignado, AS_RN.nombre as nombre_as_renovacion_asignado,
                    P.region, P.comuna,
                    P.correo_contacto, P.observaciones,
                    P.updated_at as prospecto_updated_at,
                    P.informacion_completa,
                    LN.id as id_linea_negocio,
                    LN.nombre as linea_negocio,
                    LN.codigo as codigo_linea_negocio,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion,
                    CASE
                        WHEN CL.id IS NULL THEN 'prospecto'
                        WHEN EXISTS (
                            SELECT 1 FROM Poliza PZ
                            WHERE PZ.id_cliente = CL.id
                                AND PZ.cancelada = false
                                AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                        ) THEN 'cliente_activo'
                        ELSE 'cliente_inactivo'
                    END as estado_general_cliente
                    from Prospecto P
                    inner join ProcesoComercial PC
                    on P.id = PC.id_prospecto
                    left join Cliente CL
                    on P.id = CL.id_prospecto
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    left join Usuario EJ_COM
                    on P.rut_ej_comercial_asignado = EJ_COM.rut
                    left join Usuario EJ_EV
                    on P.rut_ej_evaluacion_asignado = EJ_EV.rut
                    left join Usuario EJ_CB
                    on CL.rut_ej_cobranza_asignado = EJ_CB.rut
                    left join Usuario EJ_RN
                    on CL.rut_ej_renovacion_asignado = EJ_RN.rut
                    left join Usuario AS_RN
                    on CL.rut_as_renovacion_asignado = AS_RN.rut
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    left join PlanificacionProspecto PP
                    on P.id = PP.id_prospecto
                    left join CompanySeguros CS_PLAN
                    on PP.id_company = CS_PLAN.id
                    where PC.id = %(id_proceso)s
                '''

                params = {
                    'id_proceso': id_proceso
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowProspectoAdapter(row).to_prospecto() if row else None
            
    
    def buscar_cliente(self, id_cliente: int) -> Prospecto | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select P.id as id_prospecto,
                    CL.id as id_cliente,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    P.rut_ej_comercial_asignado, EJ_COM.nombre as nombre_ej_comercial_asignado,
                    P.rut_ej_evaluacion_asignado, EJ_EV.nombre as nombre_ej_evaluacion_asignado,
                    CL.rut_ej_cobranza_asignado, EJ_CB.nombre as nombre_ej_cobranza_asignado,
                    CL.rut_ej_renovacion_asignado, EJ_RN.nombre as nombre_ej_renovacion_asignado,
                    CL.rut_as_renovacion_asignado, AS_RN.nombre as nombre_as_renovacion_asignado,
                    P.region, P.comuna,
                    P.correo_contacto, P.observaciones,
                    P.updated_at as prospecto_updated_at,
                    P.informacion_completa,
                    LN.id as id_linea_negocio,
                    LN.nombre as linea_negocio,
                    LN.codigo as codigo_linea_negocio,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion,
                    CASE
                        WHEN CL.id IS NULL THEN 'prospecto'
                        WHEN EXISTS (
                            SELECT 1 FROM Poliza PZ
                            WHERE PZ.id_cliente = CL.id
                              AND PZ.cancelada = false
                              AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                        ) THEN 'cliente_activo'
                        ELSE 'cliente_inactivo'
                    END as estado_general_cliente
                    from Prospecto P
                    left join Cliente CL
                    on P.id = CL.id_prospecto
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    left join Usuario EJ_COM
                    on P.rut_ej_comercial_asignado = EJ_COM.rut
                    left join Usuario EJ_EV
                    on P.rut_ej_evaluacion_asignado = EJ_EV.rut
                    left join Usuario EJ_CB
                    on CL.rut_ej_cobranza_asignado = EJ_CB.rut
                    left join Usuario EJ_RN
                    on CL.rut_ej_renovacion_asignado = EJ_RN.rut
                    left join Usuario AS_RN
                    on CL.rut_as_renovacion_asignado = AS_RN.rut
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    left join PlanificacionProspecto PP
                    on P.id = PP.id_prospecto
                    left join CompanySeguros CS_PLAN
                    on PP.id_company = CS_PLAN.id
                    where CL.id = %(id_cliente)s
                '''

                params = {
                    'id_cliente': id_cliente
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowProspectoAdapter(row).to_prospecto() if row else None
                
            
    def buscar_prospecto_condominio(self, id: int) -> ProspectoCondominio | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select LN.nombre as linea_negocio,
                    LN.codigo as codigo_linea_negocio
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
                codigo_linea_negocio = row['codigo_linea_negocio']

                if codigo_linea_negocio != CODIGO_LINEA_CONDOMINIOS and linea_negocio.lower() != 'condominio':
                    return None
                
                query = '''
                    select P.id as id_prospecto,
                    CL.id as id_cliente,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    P.rut_ej_comercial_asignado, EJ_COM.nombre as nombre_ej_comercial_asignado,
                    P.rut_ej_evaluacion_asignado, EJ_EV.nombre as nombre_ej_evaluacion_asignado,
                    CL.rut_ej_cobranza_asignado, EJ_CB.nombre as nombre_ej_cobranza_asignado,
                    CL.rut_ej_renovacion_asignado, EJ_RN.nombre as nombre_ej_renovacion_asignado,
                    CL.rut_as_renovacion_asignado, AS_RN.nombre as nombre_as_renovacion_asignado,
                    P.region, P.comuna,
                    P.correo_contacto, P.observaciones,
                    P.informacion_completa,
                    P.updated_at as prospecto_updated_at,
                    PCO.updated_at as condominio_updated_at,
                    LN.id as id_linea_negocio,
                    LN.nombre as linea_negocio,
                    LN.codigo as codigo_linea_negocio,
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
                    PCO.valor_uf_m2_personalizado,
                    PCO.porcentaje_depreciacion_personalizado,
                    PCO.condominio_vertical,
                    PCO.porcentaje_espacios_comunes,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion,
                    CASE
                        WHEN CL.id IS NULL THEN 'prospecto'
                        WHEN EXISTS (
                            SELECT 1 FROM Poliza PZ
                            WHERE PZ.id_cliente = CL.id
                              AND PZ.cancelada = false
                              AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                        ) THEN 'cliente_activo'
                        ELSE 'cliente_inactivo'
                    END as estado_general_cliente
                    from Prospecto P
                    inner join ProspectoCondominio PCO
                    on P.id = PCO.id
                    left join Cliente CL
                    on P.id = CL.id_prospecto
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    left join Usuario EJ_COM
                    on P.rut_ej_comercial_asignado = EJ_COM.rut
                    left join Usuario EJ_EV
                    on P.rut_ej_evaluacion_asignado = EJ_EV.rut
                    left join Usuario EJ_CB
                    on CL.rut_ej_cobranza_asignado = EJ_CB.rut
                    left join Usuario EJ_RN
                    on CL.rut_ej_renovacion_asignado = EJ_RN.rut
                    left join Usuario AS_RN
                    on CL.rut_as_renovacion_asignado = AS_RN.rut
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

                if row is None:
                    return None

                prospecto = DictRowProspectoCondominioAdapter(row).to_prospecto_condominio()

                config_repo = RepositorioConfiguracionCondominioPostgres()

                if prospecto.valor_uf_m2_personalizado is not None:
                    prospecto.uf_por_metro_cuadrado = prospecto.valor_uf_m2_personalizado
                else:
                    valor_uf = config_repo.obtener_valor_uf_por_region(prospecto.region) if prospecto.region else None
                    prospecto.uf_por_metro_cuadrado = valor_uf

                if prospecto.porcentaje_depreciacion_personalizado is not None:
                    prospecto.porcentaje_depreciacion = prospecto.porcentaje_depreciacion_personalizado
                elif prospecto.year_construccion:
                    params_depreciacion = config_repo.obtener_parametros_depreciacion()
                    if params_depreciacion:
                        prospecto.porcentaje_depreciacion = ServicioCalculoDepreciacion.calcular(
                            prospecto.year_construccion, params_depreciacion
                        )

                return prospecto

    def registrar_prospecto_empresa(self, prospecto: ProspectoEmpresa) -> int:

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
                    'informacion_completa': informacion_completa_prospecto_empresa(prospecto)
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise ValueError('Error al registrar prospecto')

                id_prospecto: int = row['id']

                # Prospecto empresa
                query = '''
                    insert into ProspectoEmpresa(
                        id,
                        nombre_fantasia,
                        cantidad_trabajadores
                    )
                    values(
                        %(id)s,
                        %(nombre_fantasia)s,
                        %(cantidad_trabajadores)s
                    )
                '''

                params = {
                    'id': id_prospecto,
                    'nombre_fantasia': prospecto.nombre_fantasia,
                    'cantidad_trabajadores': prospecto.cantidad_trabajadores
                }

                cur.execute(query, params)

                self._insertar_giros_comerciales(cur, id_prospecto, prospecto.giros_comerciales)

                return id_prospecto

    def buscar_prospecto_empresa(self, id: int) -> ProspectoEmpresa | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select LN.nombre as linea_negocio,
                    LN.codigo as codigo_linea_negocio
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
                codigo_linea_negocio = row['codigo_linea_negocio']

                if codigo_linea_negocio != CODIGO_LINEAS_COMERCIALES and normalizar_texto(linea_negocio) != 'lineas_comerciales':
                    return None

                query = '''
                    select P.id as id_prospecto,
                    CL.id as id_cliente,
                    P.rut_riesgo, P.nombre_riesgo,
                    P.telefono_contacto, P.direccion,
                    P.rut_registrado_por, U.nombre as nombre_registrado_por,
                    P.rut_ej_comercial_asignado, EJ_COM.nombre as nombre_ej_comercial_asignado,
                    P.rut_ej_evaluacion_asignado, EJ_EV.nombre as nombre_ej_evaluacion_asignado,
                    CL.rut_ej_cobranza_asignado, EJ_CB.nombre as nombre_ej_cobranza_asignado,
                    CL.rut_ej_renovacion_asignado, EJ_RN.nombre as nombre_ej_renovacion_asignado,
                    CL.rut_as_renovacion_asignado, AS_RN.nombre as nombre_as_renovacion_asignado,
                    P.region, P.comuna,
                    P.correo_contacto, P.observaciones,
                    P.updated_at as prospecto_updated_at,
                    P.informacion_completa,
                    PEM.updated_at as empresa_updated_at,
                    PEM.nombre_fantasia,
                    PEM.cantidad_trabajadores,
                    LN.id as id_linea_negocio,
                    LN.nombre as linea_negocio,
                    LN.codigo as codigo_linea_negocio,
                    CS_PLAN.id as id_company_planificacion,
                    CS_PLAN.nombre as nombre_company_planificacion,
                    PP.prima_vigente as prima_vigente_planificacion,
                    PP.termino_vigencia as termino_vigencia_planificacion,
                    PP.monto_asegurado_vigente as monto_asegurado_vigente_planificacion,
                    PP.fecha_envio_cotizacion as fecha_envio_cotizacion_planificacion,
                    CASE
                        WHEN CL.id IS NULL THEN 'prospecto'
                        WHEN EXISTS (
                            SELECT 1 FROM Poliza PZ
                            WHERE PZ.id_cliente = CL.id
                              AND PZ.cancelada = false
                              AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                        ) THEN 'cliente_activo'
                        ELSE 'cliente_inactivo'
                    END as estado_general_cliente
                    from Prospecto P
                    inner join ProspectoEmpresa PEM
                    on P.id = PEM.id
                    left join Cliente CL
                    on P.id = CL.id_prospecto
                    inner join Usuario U
                    on P.rut_registrado_por = U.rut
                    left join Usuario EJ_COM
                    on P.rut_ej_comercial_asignado = EJ_COM.rut
                    left join Usuario EJ_EV
                    on P.rut_ej_evaluacion_asignado = EJ_EV.rut
                    left join Usuario EJ_CB
                    on CL.rut_ej_cobranza_asignado = EJ_CB.rut
                    left join Usuario EJ_RN
                    on CL.rut_ej_renovacion_asignado = EJ_RN.rut
                    left join Usuario AS_RN
                    on CL.rut_as_renovacion_asignado = AS_RN.rut
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    left join PlanificacionProspecto PP
                    on P.id = PP.id_prospecto
                    left join CompanySeguros CS_PLAN
                    on PP.id_company = CS_PLAN.id
                    where P.id = %(id)s
                '''

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return None

                giros_comerciales = self._obtener_giros_comerciales(cur, id)

                return DictRowProspectoEmpresaAdapter(row, giros_comerciales).to_prospecto_empresa()

    def crear_prospecto_empresa(self, id_prospecto: int) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    insert into ProspectoEmpresa(id)
                    values(%(id)s)
                    on conflict (id) do nothing
                '''

                params = {
                    'id': id_prospecto
                }

                cur.execute(query, params)

    def eliminar_prospecto_empresa(self, id_prospecto: int) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    delete from ProspectoEmpresa
                    where id = %(id)s
                '''

                params = {
                    'id': id_prospecto
                }

                cur.execute(query, params)

    def existe_giro_comercial_por_nombre(self, id_prospecto: int, nombre: str) -> bool:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select nombre
                    from GiroComercial
                    where id_prospecto_empresa = %(id_prospecto)s
                '''

                params = {
                    'id_prospecto': id_prospecto
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return any(
                    ServicioGirosComerciales.es_el_mismo_giro(row['nombre'], nombre)
                    for row in rows
                )

    def actualizar_prospecto_empresa(self, prospecto: ProspectoEmpresa) -> None:
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
                    'informacion_completa': informacion_completa_prospecto_empresa(prospecto),
                    'id': prospecto.id
                }

                cur.execute(query, params)

                # Datos específicos de la empresa
                query = '''
                    update ProspectoEmpresa
                    set nombre_fantasia = %(nombre_fantasia)s,
                    cantidad_trabajadores = %(cantidad_trabajadores)s
                    where id = %(id)s
                '''

                params = {
                    'nombre_fantasia': prospecto.nombre_fantasia,
                    'cantidad_trabajadores': prospecto.cantidad_trabajadores,
                    'id': prospecto.id
                }

                cur.execute(query, params)

                # Giros comerciales: la lista se reemplaza por completo
                query = '''
                    delete from GiroComercial
                    where id_prospecto_empresa = %(id)s
                '''

                params = {
                    'id': prospecto.id
                }

                cur.execute(query, params)

                self._insertar_giros_comerciales(cur, prospecto.id, prospecto.giros_comerciales)

    def _insertar_giros_comerciales(self, cur, id_prospecto: int, giros_comerciales: list[GiroComercial]) -> None:
        for giro in giros_comerciales:
            query = '''
                insert into GiroComercial(
                    id_prospecto_empresa,
                    nombre
                )
                values(
                    %(id_prospecto_empresa)s,
                    %(nombre)s
                )
            '''

            params = {
                'id_prospecto_empresa': id_prospecto,
                'nombre': giro.nombre
            }

            cur.execute(query, params)

    def _obtener_giros_comerciales(self, cur, id_prospecto: int) -> list[GiroComercial]:
        query = '''
            select id, id_prospecto_empresa, nombre
            from GiroComercial
            where id_prospecto_empresa = %(id_prospecto)s
            order by id
        '''

        params = {
            'id_prospecto': id_prospecto
        }

        cur.execute(query, params)
        rows = cur.fetchall()

        return [
            GiroComercial(
                id=row['id'],
                id_prospecto_empresa=row['id_prospecto_empresa'],
                nombre=row['nombre']
            )
            for row in rows
        ]
                

    def asignar_administrador_condominio(self, prospecto: ProspectoCondominio, id_administrador: int) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update ProspectoCondominio
                    set id_administrador = %(id_administrador)s
                    where id = %(id_prospecto)s
                '''
                params = {
                    'id_administrador': id_administrador,
                    'id_prospecto': prospecto.id
                }

                cur.execute(query, params)
