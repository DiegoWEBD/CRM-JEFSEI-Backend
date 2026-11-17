from app.dominio.proyeccion.agregado_proyeccion_proceso import AgregadoProyeccionProceso
from app.dominio.proyeccion.repositorio_proyecciones_comerciales import (
    RepositorioProyeccionesComerciales,
)
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioProyeccionesComercialesPostgres(RepositorioProyeccionesComerciales):
    """Agregados de proyección calculados en SQL.

    Un solo viaje a la base por métrica, sin recorrer procesos →
    solicitudes → cotizaciones en Python. La CTE `valores` replica la
    semántica histórica de `ServicioProyeccionesComerciales`:

    - solo cotizaciones vigentes (`fecha_vencimiento >= now()`);
    - `prima_cotizada` = suma de primas netas vigentes, redondeada;
    - `prima_potencial_estimada` = promedio de las vigentes, redondeado;
    - `prima_esperada` = potencial ya redondeado × probabilidad de cierre
      (del ejecutivo si existe, si no la del estado), redondeada; NULL sin
      probabilidad.

    Los joins de la CTE `procesos` replican los del listado de procesos
    (Prospecto, Producto `eliminado = false`, Estado, Etapa) para que un
    proceso excluido ahí tampoco aporte a los totales.
    """

    _CTE_VALORES = '''
        with procesos as (
            select PC.id,
            PC.probabilidad_cierre_ejecutivo,
            EI.probabilidad_cierre as probabilidad_cierre_estado,
            PC.fecha_estimada_cierre
            from ProcesoComercial PC
            inner join Prospecto PR
            on PC.id_prospecto = PR.id
            inner join Producto P
            on PC.id_producto = P.id
            and P.eliminado = false
            inner join EstadoInformativoProcesoComercial EI
            on PC.codigo_estado_actual = EI.codigo
            inner join EtapaProcesoComercial EPC
            on EI.codigo_etapa = EPC.codigo
            where {condicion_procesos}
        ),
        cotizaciones_vigentes as (
            select SC.id_proceso_comercial as id_proceso,
            C.prima_neta::double precision as prima_neta
            from Cotizacion C
            inner join SolicitudCotizacion SC
            on C.id_solicitud = SC.id
            inner join CompanySeguros CS
            on C.id_company = CS.id
            where C.fecha_vencimiento >= now()
            and SC.id_proceso_comercial in (select id from procesos)
        ),
        por_proceso as (
            select P.id,
            P.probabilidad_cierre_ejecutivo,
            P.probabilidad_cierre_estado,
            P.fecha_estimada_cierre,
            coalesce(sum(CV.prima_neta), 0::double precision) as suma_prima_vigente,
            count(CV.id_proceso) as cantidad_vigentes
            from procesos P
            left join cotizaciones_vigentes CV
            on CV.id_proceso = P.id
            group by P.id, P.probabilidad_cierre_ejecutivo,
            P.probabilidad_cierre_estado, P.fecha_estimada_cierre
        ),
        valores as (
            select id,
            round(suma_prima_vigente::numeric, 2) as prima_cotizada,
            case when cantidad_vigentes > 0
                then round((suma_prima_vigente / cantidad_vigentes)::numeric, 2)
                else 0::numeric
            end as prima_potencial_estimada,
            case when coalesce(probabilidad_cierre_ejecutivo, probabilidad_cierre_estado) is null
                then null
                else round(
                    (case when cantidad_vigentes > 0
                        then round((suma_prima_vigente / cantidad_vigentes)::numeric, 2)
                        else 0::numeric
                    end) * coalesce(probabilidad_cierre_ejecutivo, probabilidad_cierre_estado)::numeric, 2
                )
            end as prima_esperada,
            fecha_estimada_cierre
            from por_proceso
        )
    '''

    _TOTAL_PRIMA_COTIZADA = '''
        select coalesce(round(sum(prima_cotizada), 2), 0) as total
        from valores
    '''

    _TOTAL_PRIMA_POTENCIAL_ESTIMADA = '''
        select coalesce(round(sum(prima_potencial_estimada), 2), 0) as total
        from valores
    '''

    _TOTAL_PRIMA_ESPERADA = '''
        select coalesce(round(sum(prima_esperada), 2), 0) as total
        from valores
    '''

    _PROYECCION_POR_MES = '''
        select to_char(fecha_estimada_cierre, 'YYYY-MM') as mes,
        round(sum(prima_esperada), 2) as prima_esperada
        from valores
        where fecha_estimada_cierre is not null
        and prima_esperada is not null
        group by to_char(fecha_estimada_cierre, 'YYYY-MM')
        order by mes
    '''

    _VALORES_POR_PROCESO = '''
        select id, prima_cotizada, prima_potencial_estimada, prima_esperada
        from valores
    '''

    _TASA_CIERRE = '''
        select
            count(*) filter (
                where PC.cerrado = true
                and PC.codigo_estado_actual = 'GANADO'
            ) as oportunidades_ganadas,
            count(*) filter (
                where PC.cerrado = true
                and PC.codigo_estado_actual in ('GANADO', 'PERDIDO')
            ) as oportunidades_cerradas
        from ProcesoComercial PC
    '''

    def prima_cotizada_total_abiertos(self) -> float:
        return self._total(self._TOTAL_PRIMA_COTIZADA)

    def prima_potencial_estimada_total_abiertos(self) -> float:
        return self._total(self._TOTAL_PRIMA_POTENCIAL_ESTIMADA)

    def prima_esperada_total_abiertos(self) -> float:
        return self._total(self._TOTAL_PRIMA_ESPERADA)

    def proyeccion_prima_esperada_por_mes_abiertos(self) -> list[dict]:
        query = self._consulta_valores('PC.cerrado = false') + (
            RepositorioProyeccionesComercialesPostgres._PROYECCION_POR_MES
        )

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

                return [
                    {
                        'mes': row['mes'],
                        'prima_esperada': float(row['prima_esperada']),
                    }
                    for row in rows
                ]

    def agregados_por_proceso(self, ids_proceso: list[int]) -> dict[int, AgregadoProyeccionProceso]:
        if not ids_proceso:
            return {}

        query = self._consulta_valores('PC.id = any(%(ids_proceso)s)') + (
            RepositorioProyeccionesComercialesPostgres._VALORES_POR_PROCESO
        )

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(query, {'ids_proceso': ids_proceso})
                rows = cur.fetchall()

                return {
                    row['id']: AgregadoProyeccionProceso(
                        prima_cotizada=float(row['prima_cotizada']),
                        prima_potencial_estimada=float(row['prima_potencial_estimada']),
                        prima_esperada=(
                            None
                            if row['prima_esperada'] is None
                            else float(row['prima_esperada'])
                        ),
                    )
                    for row in rows
                }

    def tasa_cierre_oportunidades(self) -> dict:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(RepositorioProyeccionesComercialesPostgres._TASA_CIERRE)
                row = cur.fetchone()

                return {
                    'oportunidades_ganadas': row['oportunidades_ganadas'] if row else 0,
                    'oportunidades_cerradas': row['oportunidades_cerradas'] if row else 0,
                }

    def _total(self, consulta_total: str) -> float:
        query = self._consulta_valores('PC.cerrado = false') + consulta_total

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()

                return float(row['total']) if row else 0.0

    @classmethod
    def _consulta_valores(cls, condicion_procesos: str) -> str:
        return cls._CTE_VALORES.format(condicion_procesos=condicion_procesos)
