from psycopg import sql

from app.aplicacion.metricas.dto.filtros_kpi_dto import FiltrosKpiDto
from app.dominio.metricas.repositorio_kpis_comerciales import RepositorioKpisComerciales
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioKpisComercialesPostgres(RepositorioKpisComerciales):

    def _build_prospecto_filters(self, filtros: FiltrosKpiDto, params: dict) -> list[sql.Composable]:
        clauses: list[sql.Composable] = []
        if filtros.rut_ejecutivo is not None:
            clauses.append(sql.SQL("p.rut_ej_comercial_asignado = %(rut_ejecutivo)s"))
            params['rut_ejecutivo'] = filtros.rut_ejecutivo
        if filtros.id_linea_negocio is not None:
            clauses.append(sql.SQL("p.id_linea_negocio = %(id_linea_negocio)s"))
            params['id_linea_negocio'] = filtros.id_linea_negocio
        if filtros.id_sucursal is not None:
            clauses.append(sql.SQL("EXISTS (SELECT 1 FROM Usuario u WHERE u.rut = p.rut_ej_comercial_asignado AND u.id_sucursal = %(id_sucursal)s)"))
            params['id_sucursal'] = filtros.id_sucursal
        return clauses

    def _build_poliza_filters(self, filtros: FiltrosKpiDto, params: dict) -> list[sql.Composable]:
        clauses: list[sql.Composable] = []
        if filtros.year is not None:
            clauses.append(sql.SQL("EXTRACT(YEAR FROM po.fecha_emision) = %(year)s"))
            params['year'] = filtros.year
        if filtros.month is not None:
            clauses.append(sql.SQL("EXTRACT(MONTH FROM po.fecha_emision) = %(month)s"))
            params['month'] = filtros.month
        if filtros.rut_ejecutivo is not None:
            clauses.append(sql.SQL("pc.rut_ej_comercial = %(rut_ejecutivo)s"))
            params['rut_ejecutivo'] = filtros.rut_ejecutivo
        if filtros.id_producto is not None:
            clauses.append(sql.SQL("pc.id_producto = %(id_producto)s"))
            params['id_producto'] = filtros.id_producto
        if filtros.id_linea_negocio is not None:
            clauses.append(sql.SQL("pr.id_linea_negocio = %(id_linea_negocio)s"))
            params['id_linea_negocio'] = filtros.id_linea_negocio
        if filtros.id_sucursal is not None:
            clauses.append(sql.SQL("u.id_sucursal = %(id_sucursal)s"))
            params['id_sucursal'] = filtros.id_sucursal
        return clauses

    def _build_proceso_filters(self, filtros: FiltrosKpiDto, params: dict) -> list[sql.Composable]:
        clauses: list[sql.Composable] = []
        if filtros.rut_ejecutivo is not None:
            clauses.append(sql.SQL("pc.rut_ej_comercial = %(rut_ejecutivo)s"))
            params['rut_ejecutivo'] = filtros.rut_ejecutivo
        if filtros.id_producto is not None:
            clauses.append(sql.SQL("pc.id_producto = %(id_producto)s"))
            params['id_producto'] = filtros.id_producto
        if filtros.id_linea_negocio is not None:
            clauses.append(sql.SQL("pr.id_linea_negocio = %(id_linea_negocio)s"))
            params['id_linea_negocio'] = filtros.id_linea_negocio
        if filtros.id_sucursal is not None:
            clauses.append(sql.SQL("u.id_sucursal = %(id_sucursal)s"))
            params['id_sucursal'] = filtros.id_sucursal
        return clauses

    def obtener_conversion_prospectos(self, filtros: FiltrosKpiDto) -> dict:
        params: dict = {}
        prospecto_clauses = self._build_prospecto_filters(filtros, params)
        where = sql.SQL(' AND ').join(prospecto_clauses) if prospecto_clauses else sql.SQL('TRUE')
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = sql.SQL('''
                    SELECT
                        COUNT(*) AS total_prospectos,
                        COUNT(*) FILTER (
                            WHERE EXISTS (
                                SELECT 1
                                FROM Cliente c
                                JOIN Poliza po ON po.id_cliente = c.id
                                WHERE c.id_prospecto = p.id
                                  AND (po.cancelada IS NULL OR po.cancelada = false)
                            )
                        ) AS prospectos_convertidos
                    FROM Prospecto p
                    WHERE {where}
                ''').format(where=where)
                cur.execute(query, params)
                row = cur.fetchone()
                total = row['total_prospectos'] if row else 0
                convertidos = row['prospectos_convertidos'] if row else 0
                tasa = round(convertidos * 100.0 / total, 2) if total > 0 else 0.0
                return {
                    'total_prospectos': total,
                    'prospectos_convertidos': convertidos,
                    'tasa_conversion_pct': tasa,
                }

    def obtener_tasa_cierre(self, filtros: FiltrosKpiDto) -> dict:
        params: dict = {}
        proceso_clauses = self._build_proceso_filters(filtros, params)
        where = sql.SQL(' AND ').join(proceso_clauses) if proceso_clauses else sql.SQL('TRUE')
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = sql.SQL('''
                    SELECT
                        COUNT(*) FILTER (WHERE pc.cerrado = true) AS total_cerrados,
                        COUNT(*) FILTER (WHERE pc.cerrado = true AND pc.codigo_estado_actual = 'GANADO') AS ganados,
                        COUNT(*) FILTER (WHERE pc.cerrado = true AND pc.codigo_estado_actual = 'PERDIDO') AS perdidos
                    FROM ProcesoComercial pc
                    JOIN Prospecto pr ON pc.id_prospecto = pr.id
                    LEFT JOIN Usuario u ON pc.rut_ej_comercial = u.rut
                    WHERE {where}
                ''').format(where=where)
                cur.execute(query, params)
                row = cur.fetchone()
                total = row['total_cerrados'] if row else 0
                ganados = row['ganados'] if row else 0
                perdidos = row['perdidos'] if row else 0
                tasa_cierre = round(ganados * 100.0 / total, 2) if total > 0 else 0.0
                tasa_perdida = round(perdidos * 100.0 / total, 2) if total > 0 else 0.0
                return {
                    'total_procesos_cerrados': total,
                    'procesos_ganados': ganados,
                    'procesos_perdidos': perdidos,
                    'tasa_cierre_pct': tasa_cierre,
                    'tasa_perdida_pct': tasa_perdida,
                }


    def obtener_prima_vs_meta(self, filtros: FiltrosKpiDto) -> list[dict]:

        params: dict = {}
        clauses: list[sql.Composable] = []

        # Filtros sobre Usuario
        if filtros.id_sucursal is not None:
            clauses.append(sql.SQL("u.id_sucursal = %(id_sucursal)s"))
            params['id_sucursal'] = filtros.id_sucursal

        if filtros.rut_ejecutivo is not None:
            clauses.append(sql.SQL("u.rut = %(rut_ejecutivo)s"))
            params['rut_ejecutivo'] = filtros.rut_ejecutivo

        # Filtros sobre ProcesoComercial / Prospecto
        if filtros.id_producto is not None:
            clauses.append(sql.SQL("pc.id_producto = %(id_producto)s"))
            params['id_producto'] = filtros.id_producto

        if filtros.id_linea_negocio is not None:
            clauses.append(sql.SQL("pr.id_linea_negocio = %(id_linea_negocio)s"))
            params['id_linea_negocio'] = filtros.id_linea_negocio

        where = sql.SQL(' AND ').join(clauses) if clauses else sql.SQL('TRUE')

        join_year = sql.SQL("AND EXTRACT(YEAR FROM po.fecha_emision) = %(year)s") if filtros.year is not None else sql.SQL("")
        join_month = sql.SQL("AND EXTRACT(MONTH FROM po.fecha_emision) = %(month)s") if filtros.month is not None else sql.SQL("")

        where_clause = sql.SQL('WHERE {where}').format(where=where) if clauses else sql.SQL('')

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = sql.SQL('''
                    SELECT
                        u.rut,
                        u.nombre,
                        COALESCE(SUM(po.prima_neta), 0) AS prima_neta_uf,
                        u.meta_mensual_uf
                    FROM Usuario u

                    LEFT JOIN ProcesoComercial pc
                        ON pc.rut_ej_comercial = u.rut

                    LEFT JOIN Prospecto pr
                        ON pc.id_prospecto = pr.id

                    LEFT JOIN Poliza po
                        ON po.id_proceso_comercial = pc.id
                        AND (po.cancelada IS NULL OR po.cancelada = false)
                        {join_year}
                        {join_month}

                    {where_clause}

                    GROUP BY
                        u.rut,
                        u.nombre,
                        u.meta_mensual_uf

                    ORDER BY prima_neta_uf DESC
                ''').format(
                    join_year=join_year,
                    join_month=join_month,
                    where_clause=where_clause,
                )

                cur.execute(
                    query,
                    {
                        **params,
                        **({'year': filtros.year} if filtros.year is not None else {}),
                        **({'month': filtros.month} if filtros.month is not None else {}),
                    },
                )

                rows = cur.fetchall()

                result = []

                for row in rows:
                    prima = float(row['prima_neta_uf'])
                    meta = (
                        float(row['meta_mensual_uf'])
                        if row['meta_mensual_uf'] is not None
                        else 0.0
                    )

                    cumplimiento = (
                        round(prima * 100.0 / meta, 2)
                        if meta > 0
                        else 0.0
                    )

                    diferencia = round(prima - meta, 2)

                    result.append({
                        'rut_ejecutivo': row['rut'],
                        'nombre_ejecutivo': row['nombre'],
                        'prima_neta_uf': prima,
                        'meta_mensual_uf': row['meta_mensual_uf'],
                        'cumplimiento_pct': cumplimiento,
                        'diferencia_uf': diferencia,
                    })

                return result


    def obtener_tiempo_promedio_cierre(self, filtros: FiltrosKpiDto) -> dict:
        params: dict = {}
        proceso_clauses: list[sql.Composable] = [sql.SQL('pc.cerrado = true')]
        if filtros.rut_ejecutivo is not None:
            proceso_clauses.append(sql.SQL('pc.rut_ej_comercial = %(rut_ejecutivo)s'))
            params['rut_ejecutivo'] = filtros.rut_ejecutivo
        if filtros.id_producto is not None:
            proceso_clauses.append(sql.SQL('pc.id_producto = %(id_producto)s'))
            params['id_producto'] = filtros.id_producto
        if filtros.id_linea_negocio is not None:
            proceso_clauses.append(sql.SQL('pr.id_linea_negocio = %(id_linea_negocio)s'))
            params['id_linea_negocio'] = filtros.id_linea_negocio
        if filtros.id_sucursal is not None:
            proceso_clauses.append(sql.SQL('u.id_sucursal = %(id_sucursal)s'))
            params['id_sucursal'] = filtros.id_sucursal
        if filtros.year is not None:
            proceso_clauses.append(sql.SQL('EXTRACT(YEAR FROM he_cierre.fecha_registro) = %(year)s'))
            params['year'] = filtros.year
        if filtros.month is not None:
            proceso_clauses.append(sql.SQL('EXTRACT(MONTH FROM he_cierre.fecha_registro) = %(month)s'))
            params['month'] = filtros.month
        where = sql.SQL(' AND ').join(proceso_clauses)
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = sql.SQL('''
                    WITH tiempos AS (
                        SELECT
                            pc.id,
                            MIN(he_creacion.fecha_registro) AS fecha_creacion,
                            MIN(he_cierre.fecha_registro) AS fecha_cierre
                        FROM ProcesoComercial pc
                        JOIN Prospecto pr ON pc.id_prospecto = pr.id
                        LEFT JOIN Usuario u ON pc.rut_ej_comercial = u.rut
                        JOIN HistorialEstadoInformativoProcesoComercial he_creacion
                            ON he_creacion.id_proceso_comercial = pc.id
                            AND he_creacion.codigo_estado = 'OPORTUNIDAD_CREADA'
                        JOIN HistorialEstadoInformativoProcesoComercial he_cierre
                            ON he_cierre.id_proceso_comercial = pc.id
                            AND he_cierre.codigo_estado IN ('GANADO', 'PERDIDO')
                        WHERE {where}
                        GROUP BY pc.id
                    )
                    SELECT
                        COUNT(*) AS procesos_cerrados,
                        COALESCE(ROUND(AVG(EXTRACT(EPOCH FROM (fecha_cierre - fecha_creacion)) / 86400), 1), 0) AS tiempo_promedio_dias,
                        COALESCE(ROUND(MIN(EXTRACT(EPOCH FROM (fecha_cierre - fecha_creacion)) / 86400), 1), 0) AS tiempo_minimo_dias,
                        COALESCE(ROUND(MAX(EXTRACT(EPOCH FROM (fecha_cierre - fecha_creacion)) / 86400), 1), 0) AS tiempo_maximo_dias
                    FROM tiempos
                ''').format(where=where)
                cur.execute(query, params)
                row = cur.fetchone()
                return {
                    'procesos_cerrados': row['procesos_cerrados'] if row else 0,
                    'tiempo_promedio_dias': float(row['tiempo_promedio_dias']) if row else 0.0,
                    'tiempo_minimo_dias': float(row['tiempo_minimo_dias']) if row else 0.0,
                    'tiempo_maximo_dias': float(row['tiempo_maximo_dias']) if row else 0.0,
                }

    def obtener_aging_pipeline(self, filtros: FiltrosKpiDto) -> dict:
        params: dict = {}
        proceso_clauses: list[sql.Composable] = [sql.SQL('pc.cerrado = false')]
        if filtros.rut_ejecutivo is not None:
            proceso_clauses.append(sql.SQL('pc.rut_ej_comercial = %(rut_ejecutivo)s'))
            params['rut_ejecutivo'] = filtros.rut_ejecutivo
        if filtros.id_producto is not None:
            proceso_clauses.append(sql.SQL('pc.id_producto = %(id_producto)s'))
            params['id_producto'] = filtros.id_producto
        if filtros.id_linea_negocio is not None:
            proceso_clauses.append(sql.SQL('pr.id_linea_negocio = %(id_linea_negocio)s'))
            params['id_linea_negocio'] = filtros.id_linea_negocio
        if filtros.id_sucursal is not None:
            proceso_clauses.append(sql.SQL('u.id_sucursal = %(id_sucursal)s'))
            params['id_sucursal'] = filtros.id_sucursal
        where = sql.SQL(' AND ').join(proceso_clauses)
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = sql.SQL('''
                    WITH procesos_abiertos AS (
                        SELECT
                            pc.id,
                            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - he.fecha_registro)) / 86400 AS dias
                        FROM ProcesoComercial pc
                        JOIN Prospecto pr ON pc.id_prospecto = pr.id
                        LEFT JOIN Usuario u ON pc.rut_ej_comercial = u.rut
                        JOIN (
                            SELECT id_proceso_comercial, MIN(fecha_registro) AS fecha_registro
                            FROM HistorialEstadoInformativoProcesoComercial
                            WHERE codigo_estado = 'OPORTUNIDAD_CREADA'
                            GROUP BY id_proceso_comercial
                        ) he ON he.id_proceso_comercial = pc.id
                        WHERE {where}
                    ),
                    conteos AS (
                        SELECT
                            COUNT(*) AS total_abiertos,
                            COUNT(*) FILTER (WHERE dias >= 0 AND dias <= 7) AS rango_0_7,
                            COUNT(*) FILTER (WHERE dias > 7 AND dias <= 15) AS rango_8_15,
                            COUNT(*) FILTER (WHERE dias > 15 AND dias <= 30) AS rango_16_30,
                            COUNT(*) FILTER (WHERE dias > 30 AND dias <= 60) AS rango_31_60,
                            COUNT(*) FILTER (WHERE dias > 60) AS rango_60_plus
                        FROM procesos_abiertos
                    )
                    SELECT * FROM conteos
                ''').format(where=where)
                cur.execute(query, params)
                row = cur.fetchone()
                total = row['total_abiertos'] if row else 0
                rangos_data = [
                    ('0-7', row['rango_0_7'] if row else 0),
                    ('8-15', row['rango_8_15'] if row else 0),
                    ('16-30', row['rango_16_30'] if row else 0),
                    ('31-60', row['rango_31_60'] if row else 0),
                    ('60+', row['rango_60_plus'] if row else 0),
                ]
                rangos = []
                for rango_label, cantidad in rangos_data:
                    porcentaje = round(cantidad * 100.0 / total, 2) if total > 0 else 0.0
                    rangos.append({
                        'rango': rango_label,
                        'cantidad': cantidad,
                        'porcentaje': porcentaje,
                    })
                return {
                    'total_abiertos': total,
                    'rangos': rangos,
                }

    def obtener_tasa_renovacion(self, filtros: FiltrosKpiDto) -> dict:
        params: dict = {}
        clauses: list[sql.Composable] = [
            sql.SQL('po.fin_vigencia < CURRENT_TIMESTAMP'),
            sql.SQL('(po.cancelada IS NULL OR po.cancelada = false)'),
        ]
        if filtros.rut_ejecutivo is not None:
            clauses.append(sql.SQL('pc.rut_ej_comercial = %(rut_ejecutivo)s'))
            params['rut_ejecutivo'] = filtros.rut_ejecutivo
        if filtros.id_producto is not None:
            clauses.append(sql.SQL('pc.id_producto = %(id_producto)s'))
            params['id_producto'] = filtros.id_producto
        if filtros.id_linea_negocio is not None:
            clauses.append(sql.SQL('pr.id_linea_negocio = %(id_linea_negocio)s'))
            params['id_linea_negocio'] = filtros.id_linea_negocio
        if filtros.id_sucursal is not None:
            clauses.append(sql.SQL('u.id_sucursal = %(id_sucursal)s'))
            params['id_sucursal'] = filtros.id_sucursal
        if filtros.year is not None:
            clauses.append(sql.SQL('EXTRACT(YEAR FROM po.fin_vigencia) = %(year)s'))
            params['year'] = filtros.year
        if filtros.month is not None:
            clauses.append(sql.SQL('EXTRACT(MONTH FROM po.fin_vigencia) = %(month)s'))
            params['month'] = filtros.month
        where = sql.SQL(' AND ').join(clauses)
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = sql.SQL('''
                    WITH vencidas AS (
                        SELECT po.numero_poliza, po.id_cliente
                        FROM Poliza po
                        JOIN ProcesoComercial pc ON po.id_proceso_comercial = pc.id
                        JOIN Prospecto pr ON pc.id_prospecto = pr.id
                        LEFT JOIN Usuario u ON pc.rut_ej_comercial = u.rut
                        WHERE {where}
                    ),
                    renovadas AS (
                        SELECT DISTINCT v.numero_poliza
                        FROM vencidas v
                        JOIN Poliza po2 ON po2.id_cliente = v.id_cliente
                            AND po2.tipo = 'Renovación'
                            AND po2.inicio_vigencia > (SELECT fin_vigencia FROM Poliza WHERE numero_poliza = v.numero_poliza)
                            AND (po2.cancelada IS NULL OR po2.cancelada = false)
                    )
                    SELECT
                        (SELECT COUNT(*) FROM vencidas) AS polizas_vencidas,
                        (SELECT COUNT(*) FROM renovadas) AS polizas_renovadas
                ''').format(where=where)
                cur.execute(query, params)
                row = cur.fetchone()
                vencidas = row['polizas_vencidas'] if row else 0
                renovadas = row['polizas_renovadas'] if row else 0
                tasa = round(renovadas * 100.0 / vencidas, 2) if vencidas > 0 else 0.0
                return {
                    'polizas_vencidas': vencidas,
                    'polizas_renovadas': renovadas,
                    'tasa_renovacion_pct': tasa,
                }

    def obtener_prima_en_riesgo(self, filtros: FiltrosKpiDto, dias_ventana: int = 30) -> dict:
        params: dict = {'dias_ventana': dias_ventana}
        clauses: list[sql.Composable] = [
            sql.SQL("po.fin_vigencia BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '1 day' * %(dias_ventana)s"),
            sql.SQL('(po.cancelada IS NULL OR po.cancelada = false)'),
        ]
        if filtros.rut_ejecutivo is not None:
            clauses.append(sql.SQL('pc.rut_ej_comercial = %(rut_ejecutivo)s'))
            params['rut_ejecutivo'] = filtros.rut_ejecutivo
        if filtros.id_producto is not None:
            clauses.append(sql.SQL('pc.id_producto = %(id_producto)s'))
            params['id_producto'] = filtros.id_producto
        if filtros.id_linea_negocio is not None:
            clauses.append(sql.SQL('pr.id_linea_negocio = %(id_linea_negocio)s'))
            params['id_linea_negocio'] = filtros.id_linea_negocio
        if filtros.id_sucursal is not None:
            clauses.append(sql.SQL('u.id_sucursal = %(id_sucursal)s'))
            params['id_sucursal'] = filtros.id_sucursal
        where = sql.SQL(' AND ').join(clauses)
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = sql.SQL('''
                    SELECT
                        COALESCE(SUM(po.prima_neta), 0) AS prima_en_riesgo_uf,
                        COUNT(*) AS polizas_en_riesgo
                    FROM Poliza po
                    JOIN ProcesoComercial pc ON po.id_proceso_comercial = pc.id
                    JOIN Prospecto pr ON pc.id_prospecto = pr.id
                    LEFT JOIN Usuario u ON pc.rut_ej_comercial = u.rut
                    WHERE {where}
                      AND NOT EXISTS (
                          SELECT 1 FROM Poliza po2
                          WHERE po2.id_cliente = po.id_cliente
                            AND po2.tipo = 'Renovación'
                            AND po2.inicio_vigencia > po.fin_vigencia
                            AND (po2.cancelada IS NULL OR po2.cancelada = false)
                      )
                ''').format(where=where)
                cur.execute(query, params)
                row = cur.fetchone()
                return {
                    'prima_en_riesgo_uf': float(row['prima_en_riesgo_uf']) if row else 0.0,
                    'polizas_en_riesgo': row['polizas_en_riesgo'] if row else 0,
                }

    def obtener_tasa_morosidad(self, filtros: FiltrosKpiDto) -> dict:
        params: dict = {}
        clauses: list[sql.Composable] = []
        if filtros.rut_ejecutivo is not None:
            clauses.append(sql.SQL('pc.rut_ej_comercial = %(rut_ejecutivo)s'))
            params['rut_ejecutivo'] = filtros.rut_ejecutivo
        if filtros.id_producto is not None:
            clauses.append(sql.SQL('pc.id_producto = %(id_producto)s'))
            params['id_producto'] = filtros.id_producto
        if filtros.id_linea_negocio is not None:
            clauses.append(sql.SQL('pr.id_linea_negocio = %(id_linea_negocio)s'))
            params['id_linea_negocio'] = filtros.id_linea_negocio
        if filtros.id_sucursal is not None:
            clauses.append(sql.SQL('u.id_sucursal = %(id_sucursal)s'))
            params['id_sucursal'] = filtros.id_sucursal
        where = sql.SQL(' AND ').join(clauses) if clauses else sql.SQL('TRUE')
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = sql.SQL('''
                    SELECT
                        COUNT(*) AS total_cuotas,
                        COUNT(*) FILTER (WHERE c.fecha_vencimiento < CURRENT_TIMESTAMP) AS cuotas_vencidas,
                        COUNT(*) FILTER (WHERE c.fecha_vencimiento < CURRENT_TIMESTAMP AND c.pagado = false) AS cuotas_morosas
                    FROM Cuota c
                    JOIN PlanPago pp ON c.id_plan_pago = pp.id
                    JOIN Poliza po ON pp.numero_poliza = po.numero_poliza
                    JOIN ProcesoComercial pc ON po.id_proceso_comercial = pc.id
                    JOIN Prospecto pr ON pc.id_prospecto = pr.id
                    LEFT JOIN Usuario u ON pc.rut_ej_comercial = u.rut
                    WHERE {where}
                ''').format(where=where)
                cur.execute(query, params)
                row = cur.fetchone()
                total = row['total_cuotas'] if row else 0
                vencidas = row['cuotas_vencidas'] if row else 0
                morosas = row['cuotas_morosas'] if row else 0
                tasa = round(morosas * 100.0 / vencidas, 2) if vencidas > 0 else 0.0
                return {
                    'total_cuotas': total,
                    'cuotas_vencidas': vencidas,
                    'cuotas_morosas': morosas,
                    'tasa_morosidad_pct': tasa,
                }
