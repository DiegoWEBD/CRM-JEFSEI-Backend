from datetime import datetime

from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.proceso_comercial.adaptadores.dictrow_proceso_comercial_adapter import DictRowProcesoComercialAdapter


class RepositorioProcesosComercialesPostgres(RepositorioProcesosComerciales):

    def buscar(self, id: int) -> ProcesoComercial | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PC.id,
                    PC.id_prospecto,
                    PR.nombre_riesgo as nombre_cliente,
                    EI.codigo as codigo_estado,
                    EI.nombre as nombre_estado,
                    HI.fecha_registro as fecha_registro_estado,
                    EPC.codigo as codigo_etapa,
                    EPC.nombre as nombre_etapa,
                    EPC.dias_limite as dias_limite_etapa,
                    PC.cerrado,
                    PC.rut_ej_comercial,
                    EJ_COM.nombre as nombre_ej_comercial,
                    PC.rut_ej_evaluacion,
                    EJ_EV.nombre as nombre_ej_evaluacion,
                    PC.id_producto,
                    P.nombre as nombre_producto,
                    P.codigo as codigo_producto
                    from ProcesoComercial PC
                    inner join Prospecto PR
                    on PC.id_prospecto = PR.id
                    inner join Producto P
                    on PC.id_producto = P.id
                    inner join HistorialEstadoInformativoProcesoComercial HI
                    on PC.id = HI.id_proceso_comercial
                    and HI.fecha_registro = (
                        select max(HI2.fecha_registro)
                        from HistorialEstadoInformativoProcesoComercial HI2
                        where HI2.id_proceso_comercial = PC.id
                    )
                    inner join EstadoInformativoProcesoComercial EI
                    on HI.codigo_estado = EI.codigo
                    inner join EtapaProcesoComercial EPC
                    on EI.codigo_etapa = EPC.codigo
                    left join Usuario EJ_COM
                    on PC.rut_ej_comercial = EJ_COM.rut
                    left join Usuario EJ_EV
                    on PC.rut_ej_evaluacion = EJ_EV.rut
                    where PC.id = %(id)s
                '''

                params = {
                    'id': id
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowProcesoComercialAdapter(row).to_proceso_comercial() if row else None

    def obtener_procesos_comerciales(self, id_prospecto: int) -> list[ProcesoComercial]:
         with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PC.id,
                    PC.id_prospecto,
                    PR.nombre_riesgo as nombre_cliente,
                    EI.codigo as codigo_estado,
                    EI.nombre as nombre_estado,
                    HI.fecha_registro as fecha_registro_estado,
                    EPC.codigo as codigo_etapa,
                    EPC.nombre as nombre_etapa,
                    EPC.dias_limite as dias_limite_etapa,
                    PC.cerrado,
                    PC.rut_ej_comercial,
                    EJ_COM.nombre as nombre_ej_comercial,
                    PC.rut_ej_evaluacion,
                    EJ_EV.nombre as nombre_ej_evaluacion,
                    PC.id_producto,
                    P.nombre as nombre_producto,
                    P.codigo as codigo_producto
                    from ProcesoComercial PC
                    inner join Prospecto PR
                    on PC.id_prospecto = PR.id
                    inner join Producto P
                    on PC.id_producto = P.id
                    inner join HistorialEstadoInformativoProcesoComercial HI
                    on PC.id = HI.id_proceso_comercial
                    and HI.fecha_registro = (
                        select max(HI2.fecha_registro)
                        from HistorialEstadoInformativoProcesoComercial HI2
                        where HI2.id_proceso_comercial = PC.id
                    )
                    inner join EstadoInformativoProcesoComercial EI
                    on HI.codigo_estado = EI.codigo
                    inner join EtapaProcesoComercial EPC
                    on EI.codigo_etapa = EPC.codigo
                    left join Usuario EJ_COM
                    on PC.rut_ej_comercial = EJ_COM.rut
                    left join Usuario EJ_EV
                    on PC.rut_ej_evaluacion = EJ_EV.rut
                    where PC.id_prospecto = %(id_prospecto)s
                '''

                params = {
                    'id_prospecto': id_prospecto
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowProcesoComercialAdapter(row).to_proceso_comercial() for row in rows]
            
    def obtener_todos(
        self,
        texto_busqueda: str | None = None,
        ejecutivos: list[str] | None = None,
        etapas: list[str] | None = None,
        cerrado: bool | None = None,
        fecha_ingreso_etapa_desde=None,
        fecha_ingreso_etapa_hasta=None,
    ) -> list[ProcesoComercial]:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = """
                    select
                        PC.id,
                        PC.id_prospecto,
                        PR.nombre_riesgo as nombre_cliente,
                        EI.codigo as codigo_estado,
                        EI.nombre as nombre_estado,
                        HI.fecha_registro as fecha_registro_estado,
                        EPC.codigo as codigo_etapa,
                        EPC.nombre as nombre_etapa,
                        EPC.dias_limite as dias_limite_etapa,
                        PC.cerrado,
                        PC.rut_ej_comercial,
                        EJ_COM.nombre as nombre_ej_comercial,
                        PC.rut_ej_evaluacion,
                        EJ_EV.nombre as nombre_ej_evaluacion,
                        PC.id_producto,
                        P.nombre as nombre_producto,
                        P.codigo as codigo_producto
                    from ProcesoComercial PC
                    inner join Prospecto PR
                        on PC.id_prospecto = PR.id
                    inner join Producto P
                        on PC.id_producto = P.id
                    inner join HistorialEstadoInformativoProcesoComercial HI
                        on PC.id = HI.id_proceso_comercial
                        and HI.fecha_registro = (
                            select max(HI2.fecha_registro)
                            from HistorialEstadoInformativoProcesoComercial HI2
                            where HI2.id_proceso_comercial = PC.id
                        )
                    inner join EstadoInformativoProcesoComercial EI
                        on HI.codigo_estado = EI.codigo
                    inner join EtapaProcesoComercial EPC
                        on EI.codigo_etapa = EPC.codigo
                    left join Usuario EJ_COM
                        on PC.rut_ej_comercial = EJ_COM.rut
                    left join Usuario EJ_EV
                        on PC.rut_ej_evaluacion = EJ_EV.rut
                    where 1 = 1
                """

                params = []

                if texto_busqueda:
                    query += """
                        and (
                            PR.nombre_riesgo ilike %s
                            or cast(PC.id as text) ilike %s
                        )
                    """
                    busqueda = f"%{texto_busqueda}%"
                    params.extend([busqueda, busqueda])

                if ejecutivos:
                    placeholders = ", ".join(["%s"] * len(ejecutivos))
                    query += f"""
                        and PC.rut_ej_comercial in ({placeholders})
                    """
                    params.extend(ejecutivos)

                if etapas:
                    placeholders = ", ".join(["%s"] * len(etapas))
                    query += f"""
                        and EPC.codigo in ({placeholders})
                    """
                    params.extend(etapas)

                if cerrado is not None:
                    query += """
                        and PC.cerrado = %s
                    """
                    params.append(cerrado)

                if fecha_ingreso_etapa_desde is not None:
                    query += """
                        and HI.fecha_registro >= %s
                    """
                    params.append(fecha_ingreso_etapa_desde)

                if fecha_ingreso_etapa_hasta is not None:
                    query += """
                        and HI.fecha_registro <= %s
                    """
                    params.append(fecha_ingreso_etapa_hasta)

                query += """
                    order by HI.fecha_registro desc
                """

                cur.execute(query, params) # type: ignore
                rows = cur.fetchall()

                return [
                    DictRowProcesoComercialAdapter(row).to_proceso_comercial()
                    for row in rows
                ]
            
    def cerrar(self, id: int, ganado: bool, observacion: str | None, rut_usuario: str):
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                codigo_estado = 'GANADO' if ganado else 'PERDIDO'

                query = '''
                    update ProcesoComercial
                    set cerrado = %(cerrado)s,
                    codigo_estado_actual = %(codigo_estado)s
                    where id = %(id)s
                '''

                params = {
                    'id': id,
                    'cerrado': True,
                    'codigo_estado': codigo_estado,
                }

                cur.execute(query, params)

                query = '''
                    insert into HistorialEstadoInformativoProcesoComercial(
                        id_proceso_comercial, 
                        codigo_estado, 
                        fecha_registro,
                        observacion,
                        rut_registrado_por
                    )
                    values(
                        %(id_proceso_comercial)s, 
                        %(codigo_estado)s, 
                        %(fecha_registro)s,
                        %(observacion)s,
                        %(rut_registrado_por)s
                    )
                '''

                params = {
                    'id_proceso_comercial': id,
                    'codigo_estado': codigo_estado,
                    'fecha_registro': datetime.now(),
                    'observacion': observacion,
                    'rut_registrado_por': rut_usuario
                }

                cur.execute(query, params)

    def nuevo(self, tipo: str, id_prospecto: int, rut_usuario: str) -> int | None:
        ESTADO_OPORTUNIDAD_CREADA = 'OPORTUNIDAD_CREADA'
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                # Búsqueda del producto seleccionado

                query = '''
                    select id
                    from Producto
                    where codigo = %(tipo)s
                '''
                
                params = {
                    'tipo': tipo
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    raise RecursoNoEncontradoException(f'Producto con código {tipo} no encontrado')
                
                id_producto: int = row['id']

                # Creación de nuevo proceso comercial

                query = '''
                    insert into ProcesoComercial (id_prospecto, rut_ej_comercial, id_producto, codigo_estado_actual, renovacion)
                    values (%(id_prospecto)s, %(rut_ej_comercial)s, %(id_producto)s, %(codigo_estado_actual)s, %(renovacion)s)
                    returning id
                '''
                
                params = {
                    'id_prospecto': id_prospecto,
                    'rut_ej_comercial': rut_usuario,
                    'codigo_estado_actual': ESTADO_OPORTUNIDAD_CREADA,
                    'id_producto': id_producto,
                    'renovacion': False
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return None
                
                id_proceso_comercial: int = row['id']
                    
                # Registro de historial

                query = '''
                    insert into HistorialEstadoInformativoProcesoComercial (id_proceso_comercial, codigo_estado, fecha_registro, rut_registrado_por)
                    values (%(id_proceso_comercial)s, %(codigo_estado)s, %(fecha_registro)s, %(rut_registrado_por)s)
                '''
                
                params = {
                    'id_proceso_comercial': id_proceso_comercial,
                    'codigo_estado': ESTADO_OPORTUNIDAD_CREADA,
                    'fecha_registro': datetime.now(),
                    'rut_registrado_por': rut_usuario
                }

                cur.execute(query, params)

                return id_proceso_comercial
            
    def registrar_aceptacion_cliente(self, id: int, rut_usuario: str):
        ESTADO_ACEPTACION_CLIENTE = 'PROPUESTA_ACEPTADA'
        
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                    
                # Registro de historial

                query = '''
                    update ProcesoComercial
                    set codigo_estado_actual = %(codigo_estado)s
                    where id = %(id)s
                '''
                
                params = {
                    'id': id,
                    'codigo_estado': ESTADO_ACEPTACION_CLIENTE
                }

                cur.execute(query, params)

                query = '''
                    insert into HistorialEstadoInformativoProcesoComercial (id_proceso_comercial, codigo_estado, fecha_registro, rut_registrado_por)
                    values (%(id_proceso_comercial)s, %(codigo_estado)s, %(fecha_registro)s, %(rut_registrado_por)s)
                '''
                
                params = {
                    'id_proceso_comercial': id,
                    'codigo_estado': ESTADO_ACEPTACION_CLIENTE,
                    'fecha_registro': datetime.now(),
                    'rut_registrado_por': rut_usuario
                }

                cur.execute(query, params)