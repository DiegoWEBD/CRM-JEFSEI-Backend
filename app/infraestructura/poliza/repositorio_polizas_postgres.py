from datetime import datetime

from dateutil.relativedelta import relativedelta
from psycopg import sql

from app.dominio.poliza.poliza import Poliza
from app.dominio.poliza.repositorio_polizas import RepositorioPolizas
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.poliza.adapadores.dictrow_poliza_adapter import DictRowPolizaAdapter


class RepositorioPolizasPostgres(RepositorioPolizas):

    def buscar(self, numero_poliza: str) -> Poliza | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select P.numero_poliza, 
                    PRO.nombre_riesgo as nombre_cliente,
                    PRO.id as id_prospecto,
                    P.tipo, P.prima_neta, 
                    P.id_proceso_comercial,
                    P.comision_corredora_pct,
                    CS.nombre as company,
                    PR.nombre as nombre_producto,
                    P.fecha_emision,
                    P.inicio_vigencia,
                    P.fin_vigencia,
                    P.id_company,
                    P.renovacion_cotizada,
                    CASE
                        WHEN P.cancelada = true THEN 'CANCELADA'
                        WHEN P.fin_vigencia IS NULL OR P.inicio_vigencia > now() THEN 'REGISTRADA'
                        WHEN P.inicio_vigencia <= now()
                             AND P.fin_vigencia > now()
                             AND (P.fin_vigencia - now()) <= interval '60 days' THEN 'POR_VENCER'
                        WHEN P.inicio_vigencia <= now()
                             AND P.fin_vigencia > now()
                             AND (P.fin_vigencia - now()) > interval '60 days' THEN 'VIGENTE'
                        WHEN P.fin_vigencia <= now() THEN 'VENCIDA'
                        ELSE 'REGISTRADA'
                    END as estado
                    from Poliza P
                    inner join Cliente C
                    on P.id_cliente = C.id
                    inner join Prospecto PRO
                    on C.id_prospecto = PRO.id
                    inner join ProcesoComercial PC
                    on P.id_proceso_comercial = PC.id
                    inner join Producto PR
                    on PC.id_producto = PR.id
                    left join CompanySeguros CS
                    on P.id_company = CS.id
                    where P.numero_poliza = %(numero_poliza)s
                '''

                params = {
                    'numero_poliza': numero_poliza
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowPolizaAdapter(row).to_poliza() if row else None
            
    def buscar_por_proceso_comercial(self, id_proceso_comercial: int) -> Poliza | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                
                query = '''
                    select P.numero_poliza, 
                    PRO.nombre_riesgo as nombre_cliente,
                    PRO.id as id_prospecto,
                    P.tipo, P.prima_neta, 
                    P.id_proceso_comercial,
                    P.comision_corredora_pct,
                    CS.nombre as company,
                    PR.nombre as nombre_producto,
                    P.fecha_emision,
                    P.inicio_vigencia,
                    P.fin_vigencia,
                    P.id_company,
                    P.renovacion_cotizada,
                    CASE
                        WHEN P.cancelada = true THEN 'CANCELADA'
                        WHEN P.fin_vigencia IS NULL OR P.inicio_vigencia > now() THEN 'REGISTRADA'
                        WHEN P.inicio_vigencia <= now()
                             AND P.fin_vigencia > now()
                             AND (P.fin_vigencia - now()) <= interval '60 days' THEN 'POR_VENCER'
                        WHEN P.inicio_vigencia <= now()
                             AND P.fin_vigencia > now()
                             AND (P.fin_vigencia - now()) > interval '60 days' THEN 'VIGENTE'
                        WHEN P.fin_vigencia <= now() THEN 'VENCIDA'
                        ELSE 'REGISTRADA'
                    END as estado
                    from Poliza P
                    inner join Cliente C
                    on P.id_cliente = C.id
                    inner join Prospecto PRO
                    on C.id_prospecto = PRO.id
                    inner join ProcesoComercial PC
                    on P.id_proceso_comercial = PC.id
                    inner join Producto PR
                    on PC.id_producto = PR.id
                    left join CompanySeguros CS
                    on P.id_company = CS.id
                    where PC.id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                row = cur.fetchone()

                return DictRowPolizaAdapter(row).to_poliza() if row else None

    def obtener_polizas_cliente(self, id_cliente: int) -> list[Poliza]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:   

                query = '''
                    select P.numero_poliza, 
                    PRO.nombre_riesgo as nombre_cliente,
                    PRO.id as id_prospecto,
                    P.tipo, P.prima_neta, 
                    P.id_proceso_comercial,
                    P.comision_corredora_pct,
                    CS.nombre as company,
                    PR.nombre as nombre_producto,
                    P.fecha_emision,
                    P.inicio_vigencia,
                    P.fin_vigencia,
                    P.id_company,
                    P.renovacion_cotizada,
                    CASE
                        WHEN P.cancelada = true THEN 'CANCELADA'
                        WHEN P.fin_vigencia IS NULL OR P.inicio_vigencia > now() THEN 'REGISTRADA'
                        WHEN P.inicio_vigencia <= now()
                             AND P.fin_vigencia > now()
                             AND (P.fin_vigencia - now()) <= interval '60 days' THEN 'POR_VENCER'
                        WHEN P.inicio_vigencia <= now()
                             AND P.fin_vigencia > now()
                             AND (P.fin_vigencia - now()) > interval '60 days' THEN 'VIGENTE'
                        WHEN P.fin_vigencia <= now() THEN 'VENCIDA'
                        ELSE 'REGISTRADA'
                    END as estado
                    from Poliza P
                    inner join Cliente C
                    on P.id_cliente = C.id
                    inner join Prospecto PRO
                    on C.id_prospecto = PRO.id
                    inner join ProcesoComercial PC
                    on P.id_proceso_comercial = PC.id
                    inner join Producto PR
                    on PC.id_producto = PR.id
                    left join CompanySeguros CS
                    on P.id_company = CS.id
                    where P.id_cliente = %(id_cliente)s
                '''

                params = {
                    'id_cliente': id_cliente
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowPolizaAdapter(row).to_poliza() for row in rows]
    
    def polizas_gestionadas_ej_comercial_mes_actual(self, rut_ejecutivo: str) -> list[Poliza]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select P.numero_poliza, 
                    PRO.nombre_riesgo as nombre_cliente,
                    PRO.id as id_prospecto,
                    P.tipo, P.prima_neta, 
                    P.id_proceso_comercial,
                    P.comision_corredora_pct,
                    CS.id as id_company,
                    CS.nombre as company,
                    PR.nombre as nombre_producto,
                    P.fecha_emision,
                    P.inicio_vigencia,
                    P.fin_vigencia,
                    P.id_company,
                    P.renovacion_cotizada,
                    CASE
                        WHEN P.cancelada = true THEN 'CANCELADA'
                        WHEN P.fin_vigencia IS NULL OR P.inicio_vigencia > now() THEN 'REGISTRADA'
                        WHEN P.inicio_vigencia <= now()
                             AND P.fin_vigencia > now()
                             AND (P.fin_vigencia - now()) <= interval '60 days' THEN 'POR_VENCER'
                        WHEN P.inicio_vigencia <= now()
                             AND P.fin_vigencia > now()
                             AND (P.fin_vigencia - now()) > interval '60 days' THEN 'VIGENTE'
                        WHEN P.fin_vigencia <= now() THEN 'VENCIDA'
                        ELSE 'REGISTRADA'
                    END as estado
                    from Poliza P
                    inner join Cliente C
                    on P.id_cliente = C.id
                    inner join Prospecto PRO
                    on C.id_prospecto = PRO.id
                    inner join ProcesoComercial PC
                    on P.id_proceso_comercial = PC.id
                    inner join Producto PR
                    on PC.id_producto = PR.id
                    left join CompanySeguros CS
                    on P.id_company = CS.id
                    where extract(year from P.fecha_emision) = extract(year from current_date)
                    and extract(month from P.fecha_emision) = extract(month from current_date)
                    and PC.rut_ej_comercial = %(rut_ejecutivo)s
                '''

                params = {
                    'rut_ejecutivo': rut_ejecutivo
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowPolizaAdapter(row).to_poliza() for row in rows]

    def registrar_a_proceso_comercial(self, poliza: Poliza, id_proceso_comercial: int, rut_usuario: str) -> None:
        ESTADO_POLIZA_REGISTRADA = 'POLIZA_REGISTRADA'

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select C.id as id_cliente,
                    P.id as id_prospecto
                    from ProcesoComercial PC
                    inner join Prospecto P
                    on PC.id_prospecto = P.id
                    left join Cliente C
                    on P.id = C.id_prospecto
                    where PC.id = %(id_proceso_comercial)s
                '''

                params = {
                    'id_proceso_comercial': id_proceso_comercial
                }

                cur.execute(query, params)
                row = cur.fetchone()

                if row is None:
                    return
                
                id_prospecto = row['id_prospecto']
                id_cliente = row['id_cliente']

                if not id_cliente:
                    # Crear cliente en caso que no lo sea

                    query = '''
                        insert into Cliente (id_prospecto)
                        values (%(id_prospecto)s)
                        returning id
                    '''

                    params = {
                        'id_prospecto': id_prospecto
                    }

                    cur.execute(query, params)
                    row = cur.fetchone()

                    if not row:
                        return
                    
                    id_cliente = row['id']

                # Registrar póliza
                query = '''
                    insert into Poliza (
                        numero_poliza,
                        id_cliente,
                        tipo,
                        prima_neta,
                        comision_corredora_pct,
                        fecha_emision,
                        inicio_vigencia,
                        fin_vigencia,
                        id_company,
                        id_proceso_comercial,
                        cancelada,
                        renovacion_cotizada
                    )
                    values (
                        %(numero_poliza)s,
                        %(id_cliente)s,
                        %(tipo)s,
                        %(prima_neta)s,
                        %(comision_corredora_pct)s,
                        %(fecha_emision)s,
                        %(inicio_vigencia)s,
                        %(fin_vigencia)s,
                        %(id_company)s,
                        %(id_proceso_comercial)s,
                        %(cancelada)s,
                        %(renovacion_cotizada)s
                    )
                '''

                params = {
                    'numero_poliza': poliza.numero_poliza,
                    'id_cliente': id_cliente,
                    'tipo': poliza.tipo,
                    'prima_neta': poliza.prima_neta,
                    'comision_corredora_pct': poliza.comision_corredora_pct,
                    'fecha_emision': poliza.fecha_emision,
                    'inicio_vigencia': poliza.inicio_vigencia,
                    'fin_vigencia': poliza.fin_vigencia,
                    'id_company': poliza.company.id if poliza.company else None,
                    'id_proceso_comercial': id_proceso_comercial,
                    'cancelada': False,
                    'renovacion_cotizada': False
                }

                cur.execute(query, params)

                if not poliza.fin_vigencia:
                    return
                
                fecha_recordatorio_cotizacion = poliza.fin_vigencia - relativedelta(months=2)
                fecha_recordatorio_contacto = poliza.fin_vigencia - relativedelta(days=20)

                # Registrar recordatorio para comenzar a cotizar renovación

                query = '''
                    insert into Recordatorio (
                        titulo,
                        detalle,
                        prioridad,
                        completado,
                        tipo_gestion,
                        fecha_recordatorio
                    )
                    values (
                        %(titulo)s,
                        %(detalle)s,
                        %(prioridad)s,
                        %(completado)s,
                        %(tipo_gestion)s,
                        %(fecha_recordatorio)s
                    )
                    returning id
                '''

                params = {
                    'titulo': 'Iniciar cotización para renovación',
                    'detalle': f'El día {poliza.fin_vigencia.strftime("%d-%m-%Y")} vence la póliza {poliza.numero_poliza}, por lo que debe comenzar a cotizar para su renovación',
                    'prioridad': 'alta',
                    'completado': False,
                    'tipo_gestion': 'renovacion_cotizacion',
                    'fecha_recordatorio': fecha_recordatorio_cotizacion
                }

                cur.execute(query, params)
                row = cur.fetchone()
                id_recordatorio = row['id'] # type: ignore

                query = '''
                    insert into RecordatorioRenovacionPoliza (
                        id,
                        numero_poliza
                    )
                    values (
                        %(id)s,
                        %(numero_poliza)s
                    )
                '''

                params = {
                    'id': id_recordatorio,
                    'numero_poliza': poliza.numero_poliza
                }

                cur.execute(query, params)

                # Registrar recordatorio para comenzar la gestión de la renovación

                query = '''
                    insert into Recordatorio (
                        titulo,
                        detalle,
                        prioridad,
                        completado,
                        tipo_gestion,
                        fecha_recordatorio
                    )
                    values (
                        %(titulo)s,
                        %(detalle)s,
                        %(prioridad)s,
                        %(completado)s,
                        %(tipo_gestion)s,
                        %(fecha_recordatorio)s
                    )
                    returning id
                '''

                params = {
                    'titulo': 'Gestionar renovación',
                    'detalle': f'El día {poliza.fin_vigencia.strftime("%d-%m-%Y")} vence la póliza {poliza.numero_poliza}, por lo que debe gestionar su renovación',
                    'prioridad': 'alta',
                    'completado': False,
                    'tipo_gestion': 'renovacion',
                    'fecha_recordatorio': fecha_recordatorio_contacto
                }

                cur.execute(query, params)
                row = cur.fetchone()
                id_recordatorio = row['id'] # type: ignore

                query = '''
                    insert into RecordatorioRenovacionPoliza (
                        id,
                        numero_poliza
                    )
                    values (
                        %(id)s,
                        %(numero_poliza)s
                    )
                '''

                params = {
                    'id': id_recordatorio,
                    'numero_poliza': poliza.numero_poliza
                }

                cur.execute(query, params)

                # Registro de historial

                query = '''
                    insert into HistorialEstadoInformativoProcesoComercial (
                        id_proceso_comercial,
                        codigo_estado,
                        rut_registrado_por
                    )
                    select
                        %(id_proceso_comercial)s,
                        %(codigo_estado)s,
                        %(rut_registrado_por)s
                    where coalesce(
                        (
                            select codigo_estado
                            from HistorialEstadoInformativoProcesoComercial
                            where id_proceso_comercial = %(id_proceso_comercial)s
                            order by fecha_registro desc
                            limit 1
                        ),
                        ''
                    ) <> %(codigo_estado)s
                '''

                params = {
                    'id_proceso_comercial': poliza.id_proceso_comercial,
                    'codigo_estado': ESTADO_POLIZA_REGISTRADA,
                    'rut_registrado_por': rut_usuario
                }

                cur.execute(query, params)

    def obtener_polizas_panel(
        self,
        id_cliente: int | None,
        id_company: int | None,
        id_producto: int | None,
        id_linea_negocio: int | None,
        texto_busqueda: str | None,
        estado: str | None,
        rut_usuario: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[Poliza], int, dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                base_conditions: list[sql.Composable] = []
                params = {}

                if id_cliente is not None:
                    base_conditions.append(sql.SQL('P.id_cliente = %(id_cliente)s'))
                    params['id_cliente'] = id_cliente

                if id_company is not None:
                    base_conditions.append(sql.SQL('P.id_company = %(id_company)s'))
                    params['id_company'] = id_company

                if id_producto is not None:
                    base_conditions.append(sql.SQL('PR.id = %(id_producto)s'))
                    params['id_producto'] = id_producto

                if id_linea_negocio is not None:
                    base_conditions.append(sql.SQL('PR.id_linea_negocio = %(id_linea_negocio)s'))
                    params['id_linea_negocio'] = id_linea_negocio

                if texto_busqueda:
                    base_conditions.append(sql.SQL(
                        '(P.numero_poliza ILIKE %(texto_busqueda)s OR PRO.nombre_riesgo ILIKE %(texto_busqueda)s)'
                    ))
                    params['texto_busqueda'] = f'%{texto_busqueda}%'

                if rut_usuario is not None:
                    base_conditions.append(sql.SQL('''
                        (
                            PRO.rut_ej_comercial_asignado = %(rut_usuario)s
                            OR PRO.rut_ej_evaluacion_asignado = %(rut_usuario)s
                            OR C.rut_ej_renovacion_asignado = %(rut_usuario)s
                            OR C.rut_as_renovacion_asignado = %(rut_usuario)s
                            OR C.rut_ej_cobranza_asignado = %(rut_usuario)s
                        )
                    '''))
                    params['rut_usuario'] = rut_usuario

                base_where = sql.SQL(' WHERE ').join(base_conditions) if base_conditions else sql.SQL('')

                estado_filter: sql.Composable
                if estado is not None:
                    estado_filter = sql.SQL('WHERE estado = %(estado)s')
                    params['estado'] = estado
                else:
                    estado_filter = sql.SQL('')

                cte = sql.SQL('''
                    WITH base AS (
                        SELECT P.numero_poliza,
                            PRO.nombre_riesgo as nombre_cliente,
                            PRO.id as id_prospecto,
                            P.tipo, P.prima_neta,
                            P.id_proceso_comercial,
                            P.comision_corredora_pct,
                            CS.nombre as company,
                            PR.nombre as nombre_producto,
                            P.fecha_emision,
                            P.inicio_vigencia,
                            P.fin_vigencia,
                            P.id_company,
                            P.renovacion_cotizada,
                            CASE
                                WHEN P.cancelada = true THEN 'CANCELADA'
                                WHEN P.fin_vigencia IS NULL OR P.inicio_vigencia > now() THEN 'REGISTRADA'
                                WHEN P.inicio_vigencia <= now()
                                     AND P.fin_vigencia > now()
                                     AND (P.fin_vigencia - now()) <= interval '60 days' THEN 'POR_VENCER'
                                WHEN P.inicio_vigencia <= now()
                                     AND P.fin_vigencia > now()
                                     AND (P.fin_vigencia - now()) > interval '60 days' THEN 'VIGENTE'
                                WHEN P.fin_vigencia <= now() THEN 'VENCIDA'
                                ELSE 'REGISTRADA'
                            END as estado
                        FROM Poliza P
                        INNER JOIN Cliente C ON P.id_cliente = C.id
                        INNER JOIN Prospecto PRO ON C.id_prospecto = PRO.id
                        INNER JOIN ProcesoComercial PC ON P.id_proceso_comercial = PC.id
                        INNER JOIN Producto PR ON PC.id_producto = PR.id
                        LEFT JOIN CompanySeguros CS ON P.id_company = CS.id
                        {base_where}
                    )
                ''').format(base_where=base_where)

                # Conteo total
                count_query = sql.SQL('{cte} SELECT count(*) as total FROM base {estado_filter}').format(
                    cte=cte, estado_filter=estado_filter,
                )
                cur.execute(count_query, params)
                total = cur.fetchone()['total'] # type: ignore

                # KPIs
                kpi_query = sql.SQL('''
                    {cte}
                    SELECT
                        count(*) as total_polizas,
                        count(*) filter (where estado = 'CANCELADA') as canceladas,
                        count(*) filter (where estado = 'VENCIDA') as vencidas,
                        count(*) filter (where estado = 'POR_VENCER') as por_vencer,
                        count(*) filter (where estado = 'VIGENTE') as vigentes,
                        count(*) filter (where estado = 'REGISTRADA') as registradas,
                        coalesce(sum(prima_neta), 0) as prima_neta_total,
                        coalesce(sum(prima_neta) filter (where estado in ('VIGENTE', 'POR_VENCER')), 0) as prima_vigente,
                        coalesce(sum(prima_neta * comision_corredora_pct), 0) as comision_total
                    FROM base
                ''').format(cte=cte)
                cur.execute(kpi_query, params)
                kpi_row = cur.fetchone()

                if not kpi_row:
                    raise ValueError('Error en la base de datos')

                kpis = {
                    'total_polizas': kpi_row['total_polizas'],
                    'vigentes': kpi_row['vigentes'],
                    'por_vencer': kpi_row['por_vencer'],
                    'vencidas': kpi_row['vencidas'],
                    'canceladas': kpi_row['canceladas'],
                    'registradas': kpi_row['registradas'],
                    'prima_neta_total': round(kpi_row['prima_neta_total'], 2),
                    'prima_vigente': round(kpi_row['prima_vigente'], 2),
                    'comision_total': round(kpi_row['comision_total'], 2),
                }

                # Datos paginados
                offset = (pagina - 1) * tamano_pagina
                params['tamano_pagina'] = tamano_pagina
                params['offset'] = offset

                data_query = sql.SQL('''
                    {cte}
                    SELECT * FROM base
                    {estado_filter}
                    ORDER BY fecha_emision DESC NULLS LAST
                    LIMIT %(tamano_pagina)s OFFSET %(offset)s
                ''').format(cte=cte, estado_filter=estado_filter)
                cur.execute(data_query, params)
                rows = cur.fetchall()

                polizas = [DictRowPolizaAdapter(row).to_poliza() for row in rows]

                return polizas, total, kpis

    def actualizar_cancelada(self, numero_poliza: str, cancelada: bool) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update Poliza
                    set cancelada = %(cancelada)s
                    where numero_poliza = %(numero_poliza)s
                '''

                params = {
                    'numero_poliza': numero_poliza,
                    'cancelada': cancelada
                }

                cur.execute(query, params)

    def actualizar(
        self,
        numero_poliza: str,
        tipo: str,
        prima_neta: float,
        comision_corredora_pct: float,
        fecha_emision: datetime | None,
        inicio_vigencia: datetime | None,
        fin_vigencia: datetime | None,
        id_company: int | None,
    ) -> None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    update Poliza
                    set tipo = %(tipo)s,
                        prima_neta = %(prima_neta)s,
                        comision_corredora_pct = %(comision_corredora_pct)s,
                        fecha_emision = %(fecha_emision)s,
                        inicio_vigencia = %(inicio_vigencia)s,
                        fin_vigencia = %(fin_vigencia)s,
                        id_company = %(id_company)s
                    where numero_poliza = %(numero_poliza)s
                '''

                params = {
                    'numero_poliza': numero_poliza,
                    'tipo': tipo,
                    'prima_neta': prima_neta,
                    'comision_corredora_pct': comision_corredora_pct,
                    'fecha_emision': fecha_emision,
                    'inicio_vigencia': inicio_vigencia,
                    'fin_vigencia': fin_vigencia,
                    'id_company': id_company,
                }

                cur.execute(query, params)
