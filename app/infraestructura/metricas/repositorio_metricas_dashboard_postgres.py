from datetime import date

from app.dominio.metricas.repositorio_metricas_dashboard import (
    RepositorioMetricasDashboard,
)
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioMetricasDashboardPostgres(RepositorioMetricasDashboard):

    def obtener_prima_neta_mes(self, year: int, mes: int) -> float:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select coalesce(sum(prima_neta), 0) as total
                    from Poliza
                    where extract(year from fecha_emision) = %(year)s
                      and extract(month from fecha_emision) = %(mes)s
                      and (cancelada is null or cancelada = false)
                    ''',
                    {'year': year, 'mes': mes},
                )
                row = cur.fetchone()

                if row is None:
                    return 0

                return float(row['total'])

    def obtener_prima_neta_rango(
        self, desde: date, hasta: date
    ) -> float:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select coalesce(sum(prima_neta), 0) as total
                    from Poliza
                    where fecha_emision >= %(desde)s
                      and fecha_emision < %(hasta)s
                      and (cancelada is null or cancelada = false)
                    ''',
                    {'desde': desde, 'hasta': hasta},
                )
                row = cur.fetchone()

                if row is None:
                    return 0

                return float(row['total'])

    def obtener_tendencia_12_meses(self) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select
                      to_char(fecha_emision, 'Mon') as mes,
                      extract(month from fecha_emision) as mes_num,
                      extract(year from fecha_emision) as year,
                      coalesce(sum(prima_neta), 0) as prima_neta
                    from Poliza
                    where fecha_emision >= date_trunc('month', current_date - interval '11 months')
                      and (cancelada is null or cancelada = false)
                    group by year, mes_num, mes
                    order by year, mes_num
                    '''
                )
                return cur.fetchall()

    def obtener_prima_por_compania(
        self, year: int, mes: int
    ) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select cs.nombre, coalesce(sum(p.prima_neta), 0) as valor
                    from Poliza p
                    join CompanySeguros cs on p.id_company = cs.id
                    where extract(year from p.fecha_emision) = %(year)s
                      and extract(month from p.fecha_emision) = %(mes)s
                      and (p.cancelada is null or p.cancelada = false)
                    group by cs.nombre
                    order by valor desc
                    ''',
                    {'year': year, 'mes': mes},
                )
                return cur.fetchall()

    def obtener_prima_por_ejecutivo(
        self, year: int, mes: int
    ) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select u.nombre, coalesce(sum(p.prima_neta), 0) as valor
                    from Poliza p
                    join ProcesoComercial pc on p.id_proceso_comercial = pc.id
                    join Usuario u on pc.rut_ej_comercial = u.rut
                    where extract(year from p.fecha_emision) = %(year)s
                      and extract(month from p.fecha_emision) = %(mes)s
                      and (p.cancelada is null or p.cancelada = false)
                    group by u.nombre
                    order by valor desc
                    ''',
                    {'year': year, 'mes': mes},
                )
                return cur.fetchall()

    def obtener_prima_por_producto(
        self, year: int, mes: int
    ) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select pr.nombre, coalesce(sum(p.prima_neta), 0) as valor
                    from Poliza p
                    join ProcesoComercial pc on p.id_proceso_comercial = pc.id
                    join Producto pr on pc.id_producto = pr.id
                    where extract(year from p.fecha_emision) = %(year)s
                      and extract(month from p.fecha_emision) = %(mes)s
                      and (p.cancelada is null or p.cancelada = false)
                    group by pr.nombre
                    order by valor desc
                    ''',
                    {'year': year, 'mes': mes},
                )
                return cur.fetchall()

    def obtener_actividades_comerciales(
        self, year: int, mes: int
    ) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select
                      ru.tipo_gestion as tipo,
                      count(*) filter (where ru.completado = true) as concretadas,
                      count(*) filter (where ru.completado = false) as pendientes
                    from RecordatorioUsuario ru
                    where extract(year from ru.fecha_recordatorio) = %(year)s
                      and extract(month from ru.fecha_recordatorio) = %(mes)s
                    group by ru.tipo_gestion
                    order by ru.tipo_gestion
                    ''',
                    {'year': year, 'mes': mes},
                )
                return cur.fetchall()

    def obtener_resumen_actividades(
        self, year: int, mes: int
    ) -> dict:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select
                      count(*) as agendadas,
                      count(*) filter (where ru.completado = true) as concretadas,
                      count(*) filter (where ru.completado = false) as pendientes
                    from RecordatorioUsuario ru
                    where extract(year from ru.fecha_recordatorio) = %(year)s
                      and extract(month from ru.fecha_recordatorio) = %(mes)s
                    ''',
                    {'year': year, 'mes': mes},
                )
                row = cur.fetchone()

                if row is None:
                    return {
                        'agendadas': 0,
                        'concretadas': 0,
                        'pendientes': 0
                    }

                total = row['agendadas']

                row['porcentaje_cumplimiento'] = (
                    round(row['concretadas'] * 100.0 / total, 0)
                    if total > 0
                    else 0
                )

                return row

    def obtener_polizas_por_comuna(self) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                        select coalesce(PR.comuna, 'Desconocida') as nombre,
                        count(*) as cantidad
                        from Poliza P
                        join Cliente C
                        on P.id_cliente = C.id
                        inner join Prospecto PR
                        on C.id_prospecto = PR.id
                        where P.cancelada is null or P.cancelada = false
                        group by coalesce(PR.comuna, 'Desconocida')
                        order by cantidad desc
                    '''
                )
                return cur.fetchall()

    def obtener_polizas_por_producto(self) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                        select pr.nombre, count(*) as cantidad
                        from Poliza p
                        join ProcesoComercial pc on p.id_proceso_comercial = pc.id
                        join Producto pr on pc.id_producto = pr.id
                        where p.cancelada is null or p.cancelada = false
                        group by pr.nombre
                        order by cantidad desc
                    '''
                )
                return cur.fetchall()

    def obtener_kpis_evaluacion(self) -> dict:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    with procesos_con_evaluacion as (
                    select distinct pc.id
                    from ProcesoComercial pc
                    join SolicitudCotizacion sc
                        on pc.id = sc.id_proceso_comercial
                    ),
                    procesos_con_poliza as (
                    select distinct pc.id
                    from ProcesoComercial pc
                    join Poliza p on pc.id = p.id_proceso_comercial
                    where p.cancelada is null or p.cancelada = false
                    )
                    select
                    count(pe.id) as total_proyectos,
                    count(pp.id) as convertidos
                    from procesos_con_evaluacion pe
                    left join procesos_con_poliza pp on pe.id = pp.id
                    '''
                )
                row = cur.fetchone()

                if row is None:
                    return {
                        'total_proyectos': 0,
                        'monto_total_uf': 0,
                        'tasa_conversion': 0
                    }

                total = row['total_proyectos']
                return {
                    'total_proyectos': total,
                    #'monto_total_uf': self._obtener_monto_total_uf(),
                    'monto_total_uf': 0,
                    'tasa_conversion': (
                        round(row['convertidos'] * 100.0 / total, 0)
                        if total > 0
                        else 0
                    ),
                }

    def _obtener_monto_total_uf(self) -> float:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    select coalesce(sum(ver.monto_asegurado), 0) as total
                    from SolicitudEvaluacionRiesgo ser
                    join EvaluacionRiesgo er on ser.id = er.id_solicitud
                    join VersionEvaluacionRiesgo ver
                      on er.id = ver.id_evaluacion_riesgo
                    '''
                )
                row = cur.fetchone()

                return float(row['total'] if row is not None else 0)

    def obtener_evaluacion_por_compania(self) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                return []
                
                cur.execute(
                    '''
                    select cs.nombre, count(distinct ser.id) as cantidad
                    from SolicitudEvaluacionRiesgo ser
                    join ProcesoComercial pc on ser.id_proceso_comercial = pc.id
                    join Prospecto pr on pc.id_prospecto = pr.id
                    left join Poliza p on pc.id = p.id_proceso_comercial
                    left join CompanySeguros cs on p.id_company = cs.id
                    group by cs.nombre
                    order by cantidad desc
                    '''
                )
                return cur.fetchall()

    def obtener_evaluacion_por_producto(self) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                return []
            
                cur.execute(
                    '''
                    select pr.nombre, count(distinct ser.id) as cantidad
                    from SolicitudEvaluacionRiesgo ser
                    join ProcesoComercial pc on ser.id_proceso_comercial = pc.id
                    join Producto pr on pc.id_producto = pr.id
                    group by pr.nombre
                    order by cantidad desc
                    '''
                )
                return cur.fetchall()
