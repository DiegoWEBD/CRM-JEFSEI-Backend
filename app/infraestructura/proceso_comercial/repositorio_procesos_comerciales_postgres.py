from datetime import datetime, timezone

from psycopg import sql

from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.proceso_comercial.adaptadores.dictrow_proceso_comercial_adapter import DictRowProcesoComercialAdapter
from app.infraestructura.proceso_comercial.adaptadores.dictrow_reporte_proceso_comercial_adapter import DictRowReporteProcesoComercialAdapter


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
                    and P.eliminado = false
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

    def obtener_procesos_comerciales(self, id_prospecto: int, abiertos: bool | None = None) -> list[ProcesoComercial]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = """
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
                    and P.eliminado = false
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

                params: dict = {}

                query += """
                    and PC.id_prospecto = %(id_prospecto)s
                """
                params["id_prospecto"] = id_prospecto

                if abiertos is True:
                    query += """
                        and PC.cerrado = false
                    """
                elif abiertos is False:
                    query += """
                        and PC.cerrado = true
                    """

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowProcesoComercialAdapter(row).to_proceso_comercial() for row in rows]
            
    def obtener_todos(
        self,
        texto_busqueda: str | None = None,
        ejecutivos: list[str] | None = None,
        etapas: list[str] | None = None,
        estados_comerciales: list[str] | None = None,
        estado_semaforo: list[str] | None = None,
        estado_proceso: str | None = None,
        cerrado: bool | None = None,
        fecha_ingreso_etapa_desde=None,
        fecha_ingreso_etapa_hasta=None,
        pagina: int = 1,
        tamano_pagina: int = 15,
    ) -> dict:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                base_cte = sql.SQL("""
                    WITH base AS (
                        SELECT
                            PC.id,
                            PC.id_prospecto,
                            PR.nombre_riesgo AS nombre_cliente,
                            EI.codigo AS codigo_estado,
                            EI.nombre AS nombre_estado,
                            HI.fecha_registro AS fecha_registro_estado,
                            EPC.codigo AS codigo_etapa,
                            EPC.nombre AS nombre_etapa,
                            EPC.dias_limite AS dias_limite_etapa,
                            PC.cerrado,
                            PC.rut_ej_comercial,
                            EJ_COM.nombre AS nombre_ej_comercial,
                            PC.rut_ej_evaluacion,
                            EJ_EV.nombre AS nombre_ej_evaluacion,
                            PC.id_producto,
                            P.nombre AS nombre_producto,
                            P.codigo AS codigo_producto,
                            (
                                SELECT MIN(HI2.fecha_registro)
                                FROM HistorialEstadoInformativoProcesoComercial HI2
                                INNER JOIN EstadoInformativoProcesoComercial EI2
                                    ON HI2.codigo_estado = EI2.codigo
                                WHERE HI2.id_proceso_comercial = PC.id
                                  AND EI2.codigo_etapa = EPC.codigo
                            ) AS fecha_ingreso_etapa
                        FROM ProcesoComercial PC
                        INNER JOIN Prospecto PR ON PC.id_prospecto = PR.id
                        INNER JOIN Producto P ON PC.id_producto = P.id
                        AND P.eliminado = false
                        INNER JOIN HistorialEstadoInformativoProcesoComercial HI
                            ON PC.id = HI.id_proceso_comercial
                            AND HI.fecha_registro = (
                                SELECT MAX(HI3.fecha_registro)
                                FROM HistorialEstadoInformativoProcesoComercial HI3
                                WHERE HI3.id_proceso_comercial = PC.id
                            )
                        INNER JOIN EstadoInformativoProcesoComercial EI
                            ON HI.codigo_estado = EI.codigo
                        INNER JOIN EtapaProcesoComercial EPC
                            ON EI.codigo_etapa = EPC.codigo
                        LEFT JOIN Usuario EJ_COM ON PC.rut_ej_comercial = EJ_COM.rut
                        LEFT JOIN Usuario EJ_EV ON PC.rut_ej_evaluacion = EJ_EV.rut
                    )
                """)

                params: dict = {}
                condiciones: list[sql.Composable] = []

                if texto_busqueda:
                    condiciones.append(sql.SQL("""
                        (
                            base.nombre_cliente ILIKE %(texto_busqueda)s
                            OR CAST(base.id AS TEXT) ILIKE %(texto_busqueda)s
                            OR base.nombre_ej_comercial ILIKE %(texto_busqueda)s
                            OR base.nombre_producto ILIKE %(texto_busqueda)s
                        )
                    """))
                    params["texto_busqueda"] = f"%{texto_busqueda}%"

                if ejecutivos:
                    placeholders = ", ".join(
                        f"%(ejecutivo_{i})s" for i in range(len(ejecutivos))
                    )
                    condiciones.append(sql.SQL(f"base.rut_ej_comercial IN ({placeholders})"))
                    for i, rut in enumerate(ejecutivos):
                        params[f"ejecutivo_{i}"] = rut

                if etapas:
                    placeholders = ", ".join(
                        f"%(etapa_{i})s" for i in range(len(etapas))
                    )
                    condiciones.append(sql.SQL(f"base.codigo_etapa IN ({placeholders})"))
                    for i, codigo in enumerate(etapas):
                        params[f"etapa_{i}"] = codigo

                if estados_comerciales:
                    placeholders = ", ".join(
                        f"%(estado_comercial_{i})s" for i in range(len(estados_comerciales))
                    )
                    condiciones.append(sql.SQL(f"base.codigo_estado IN ({placeholders})"))
                    for i, codigo in enumerate(estados_comerciales):
                        params[f"estado_comercial_{i}"] = codigo

                if cerrado is not None:
                    condiciones.append(sql.SQL("base.cerrado = %(cerrado)s"))
                    params["cerrado"] = cerrado

                if fecha_ingreso_etapa_desde is not None:
                    condiciones.append(sql.SQL("base.fecha_ingreso_etapa >= %(fecha_desde)s"))
                    params["fecha_desde"] = fecha_ingreso_etapa_desde

                if fecha_ingreso_etapa_hasta is not None:
                    condiciones.append(sql.SQL("base.fecha_ingreso_etapa <= %(fecha_hasta)s"))
                    params["fecha_hasta"] = fecha_ingreso_etapa_hasta

                if estado_proceso:
                    if estado_proceso == "abiertos":
                        condiciones.append(sql.SQL("base.cerrado = FALSE"))
                    elif estado_proceso == "ganados":
                        condiciones.append(sql.SQL("base.cerrado = TRUE AND base.codigo_estado = 'GANADO'"))
                    elif estado_proceso == "perdidos":
                        condiciones.append(sql.SQL("base.cerrado = TRUE AND base.codigo_estado = 'PERDIDO'"))

                where_sql = sql.SQL("")
                if condiciones:
                    where_sql = sql.SQL("WHERE ") + sql.SQL(" AND ").join(condiciones)

                semaforo_cte_columns = sql.SQL("""
                        SELECT *,
                            CASE
                                WHEN base.cerrado THEN 'NO_APLICA'
                                WHEN base.fecha_ingreso_etapa IS NULL OR base.dias_limite_etapa IS NULL THEN 'NO_APLICA'
                                WHEN EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa) / base.dias_limite_etapa < 0.70 THEN 'VERDE'
                                WHEN EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa) / base.dias_limite_etapa <= 1.0 THEN 'AMARILLO'
                                ELSE 'ROJO'
                            END AS estado_semaforo,
                            CASE
                                WHEN base.cerrado OR base.fecha_ingreso_etapa IS NULL OR base.dias_limite_etapa IS NULL THEN NULL
                                ELSE EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa)::int
                            END AS dias_transcurridos,
                            CASE
                                WHEN base.cerrado OR base.fecha_ingreso_etapa IS NULL OR base.dias_limite_etapa IS NULL THEN NULL
                                ELSE ROUND((EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa) / base.dias_limite_etapa)::numeric, 4)
                            END AS porcentaje_sla_consumido,
                            CASE
                                WHEN base.cerrado OR base.fecha_ingreso_etapa IS NULL OR base.dias_limite_etapa IS NULL THEN NULL
                                ELSE (base.dias_limite_etapa - EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa))::int
                            END AS dias_restantes,
                            CASE
                                WHEN base.cerrado OR base.fecha_ingreso_etapa IS NULL OR base.dias_limite_etapa IS NULL THEN NULL
                                ELSE (EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa) - base.dias_limite_etapa)::int
                            END AS dias_atraso,
                            CASE
                                WHEN base.cerrado THEN NULL
                                WHEN base.fecha_ingreso_etapa IS NULL OR base.dias_limite_etapa IS NULL THEN NULL
                                WHEN EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa) / base.dias_limite_etapa < 0.70
                                    THEN 'Dentro del plazo (' || EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa)::text || ' de ' || base.dias_limite_etapa::text || ' días)'
                                WHEN EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa) / base.dias_limite_etapa <= 1.0
                                    THEN 'Próximo a vencer (' || EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa)::text || ' de ' || base.dias_limite_etapa::text || ' días)'
                                ELSE 'Fuera de plazo (+' || (EXTRACT(DAY FROM (NOW() AT TIME ZONE 'UTC') - base.fecha_ingreso_etapa)::int - base.dias_limite_etapa)::text || ' días de atraso)'
                            END AS mensaje_semaforo
                        FROM base
                """)

                semaforo_cte = sql.SQL(""",
                    con_semaforo AS (
                        {semaforo_cte_columns}
                        {where_sql}
                    )
                """).format(
                    semaforo_cte_columns=semaforo_cte_columns,
                    where_sql=where_sql,
                )

                semaforo_cte_global = sql.SQL(""",
                    con_semaforo_global AS (
                        {semaforo_cte_columns}
                    )
                """).format(
                    semaforo_cte_columns=semaforo_cte_columns,
                )

                if estado_semaforo:
                    placeholders_semaforo = ", ".join(
                        f"%(sem_{i})s" for i in range(len(estado_semaforo))
                    )
                    where_semaforo = sql.SQL(f"WHERE con_semaforo.estado_semaforo IN ({placeholders_semaforo})")
                    for i, sem in enumerate(estado_semaforo):
                        params[f"sem_{i}"] = sem
                else:
                    where_semaforo = sql.SQL("")

                global_count_query = sql.SQL("""
                    {base_cte}
                    {semaforo_cte_global}
                    SELECT
                        COUNT(*) AS total,
                        COUNT(*) FILTER (WHERE NOT cerrado) AS abiertos,
                        COUNT(*) FILTER (WHERE cerrado AND codigo_estado = 'GANADO') AS ganados,
                        COUNT(*) FILTER (WHERE cerrado AND codigo_estado = 'PERDIDO') AS perdidos,
                        COUNT(*) FILTER (WHERE estado_semaforo = 'VERDE') AS verde,
                        COUNT(*) FILTER (WHERE estado_semaforo = 'AMARILLO') AS amarillo,
                        COUNT(*) FILTER (WHERE estado_semaforo = 'ROJO') AS rojo
                    FROM con_semaforo_global
                """).format(
                    base_cte=base_cte,
                    semaforo_cte_global=semaforo_cte_global,
                )

                cur.execute(global_count_query)
                global_row = cur.fetchone()

                contadores_estado = {
                    "todas": global_row["total"] if global_row else 0,
                    "abiertos": global_row["abiertos"] if global_row else 0,
                    "ganados": global_row["ganados"] if global_row else 0,
                    "perdidos": global_row["perdidos"] if global_row else 0,
                    "verde": global_row["verde"] if global_row else 0,
                    "amarillo": global_row["amarillo"] if global_row else 0,
                    "rojo": global_row["rojo"] if global_row else 0,
                }

                count_query = sql.SQL("""
                    {base_cte}
                    {semaforo_cte}
                    SELECT COUNT(*) AS total
                    FROM con_semaforo
                    {where_semaforo}
                """).format(
                    base_cte=base_cte,
                    semaforo_cte=semaforo_cte,
                    where_semaforo=where_semaforo,
                )

                cur.execute(count_query, params)
                row_count = cur.fetchone()

                total = row_count["total"] if row_count else 0
                total_paginas = (total + tamano_pagina - 1) // tamano_pagina if total else 0

                offset = (pagina - 1) * tamano_pagina

                order_sql = sql.SQL("""
                    ORDER BY
                        CASE con_semaforo.estado_semaforo
                            WHEN 'ROJO' THEN 0
                            WHEN 'AMARILLO' THEN 1
                            WHEN 'VERDE' THEN 2
                            ELSE 3
                        END,
                        con_semaforo.fecha_registro_estado DESC
                """)

                data_query = sql.SQL("""
                    {base_cte}
                    {semaforo_cte}
                    SELECT con_semaforo.*
                    FROM con_semaforo
                    {where_semaforo}
                    {order_sql}
                    LIMIT %(tamano_pagina)s OFFSET %(offset)s
                """).format(
                    base_cte=base_cte,
                    semaforo_cte=semaforo_cte,
                    where_semaforo=where_semaforo,
                    order_sql=order_sql,
                )

                data_params = {**params, "tamano_pagina": tamano_pagina, "offset": offset}
                cur.execute(data_query, data_params)
                rows = cur.fetchall()

                data = [
                    DictRowReporteProcesoComercialAdapter(row).to_reporte()
                    for row in rows
                ]

                return {
                    "data": data,
                    "total": total,
                    "pagina": pagina,
                    "tamano_pagina": tamano_pagina,
                    "total_paginas": total_paginas,
                    "contadores_estado": contadores_estado,
                }
            
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
                    'fecha_registro': datetime.now(tz=timezone.utc),
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
                    and eliminado = false
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
                    'fecha_registro': datetime.now(tz=timezone.utc),
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
                    'fecha_registro': datetime.now(tz=timezone.utc),
                    'rut_registrado_por': rut_usuario
                }

                cur.execute(query, params)