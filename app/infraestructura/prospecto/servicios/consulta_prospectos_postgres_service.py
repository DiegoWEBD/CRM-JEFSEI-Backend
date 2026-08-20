import math
from typing import Optional

from psycopg import sql

from app.aplicacion.prospecto.dto.prospecto_resumen import ProspectoResumen
from app.aplicacion.prospecto.servicios.consulta_prospectos_service import ConsultaProspectosService
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.prospecto.adaptadores.dictrows_prospectos_resumen_adapter import DictRowsProspectoResumenAdapter


class ConsultaProspectosPostgresService(ConsultaProspectosService):

    _BASE_QUERY = sql.SQL('''
        select distinct on (P.nombre_riesgo, PC.id) 
        P.id,
        PC.id as id_proceso_comercial,
        C.id as id_cliente,
        P.rut_riesgo,
        P.nombre_riesgo,
        P.comuna,
        AC.nombre_administrador,
        LN.nombre as linea_negocio,
        EJ_COM.nombre as ejecutivo_comercial,
        EI.codigo as codigo_estado,
        EI.nombre as nombre_estado,
        HE.fecha_registro as fecha_ultima_accion,
        CASE
            WHEN C.id IS NULL THEN 'prospecto'
            WHEN EXISTS (
                SELECT 1 FROM Poliza PZ
                WHERE PZ.id_cliente = C.id
                  AND PZ.cancelada = false
                  AND PZ.inicio_vigencia <= CURRENT_TIMESTAMP
                  AND PZ.fin_vigencia > CURRENT_TIMESTAMP
            ) THEN 'cliente_activo'
            ELSE 'cliente_inactivo'
        END as estado_general_cliente
        from Prospecto P
        left join Cliente C
        on P.id = C.id_prospecto
        left join ProspectoCondominio PCO
        on P.id = PCO.id
        left join AdministradorCondominio AC
        on PCO.id_administrador = AC.id
        inner join LineaNegocio LN 
        on P.id_linea_negocio = LN.id
        left join ProcesoComercial PC
        on P.id = PC.id_prospecto
        left join HistorialEstadoInformativoProcesoComercial HE
        on PC.id = HE.id_proceso_comercial
        left join EstadoInformativoProcesoComercial EI
        on HE.codigo_estado = EI.codigo
        left join Usuario EJ_COM
        on P.rut_ej_comercial_asignado = EJ_COM.rut
        {where_clause}
        order by P.nombre_riesgo, PC.id, HE.fecha_registro desc
    ''')

    @staticmethod
    def _filtrar_joins(texto_busqueda: Optional[str]) -> sql.Composable:
        joins = sql.SQL('''
            left join Cliente C
            on P.id = C.id_prospecto
        ''')

        if texto_busqueda:
            joins = sql.Composed([
                joins,
                sql.SQL('''
                    left join ProspectoCondominio PCO
                    on P.id = PCO.id
                    left join AdministradorCondominio AC
                    on PCO.id_administrador = AC.id
                    inner join LineaNegocio LN
                    on P.id_linea_negocio = LN.id
                    left join ProcesoComercial PC
                    on P.id = PC.id_prospecto
                    left join HistorialEstadoInformativoProcesoComercial HE
                    on PC.id = HE.id_proceso_comercial
                    left join EstadoInformativoProcesoComercial EI
                    on HE.codigo_estado = EI.codigo
                    left join Usuario EJ_COM
                    on PC.rut_ej_comercial = EJ_COM.rut
                ''')
            ])

        return joins

    def _construir_where(
        self,
        filtro: Optional[str],
        texto_busqueda: Optional[str],
        rut_usuario: Optional[str],
        params: dict,
        region: Optional[str] = None,
        comuna: Optional[str] = None,
    ) -> sql.Composable:
        condiciones: list[sql.Composable] = []

        if rut_usuario:
            condiciones.append(sql.SQL('''
                (
                    P.rut_ej_comercial_asignado = %(rut_usuario)s
                    or P.rut_ej_evaluacion_asignado = %(rut_usuario)s
                    or C.rut_ej_renovacion_asignado = %(rut_usuario)s
                    or C.rut_ej_cobranza_asignado = %(rut_usuario)s
                )
            '''))
            params["rut_usuario"] = rut_usuario

        if filtro and filtro.lower() != 'todos':
            filtro_normalizado = filtro.lower()

            if filtro_normalizado == 'prospecto':
                condiciones.append(sql.SQL('C.id IS NULL'))

            elif filtro_normalizado == 'cliente_activo':
                condiciones.append(sql.SQL('''
                    (
                        C.id IS NOT NULL AND EXISTS (
                            SELECT 1 FROM Poliza PZ
                            WHERE PZ.id_cliente = C.id
                              AND PZ.cancelada = false
                              AND PZ.inicio_vigencia <= CURRENT_TIMESTAMP
                              AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                        )
                    )
                '''))

            elif filtro_normalizado == 'cliente_inactivo':
                condiciones.append(sql.SQL('''
                    (
                        C.id IS NOT NULL AND NOT EXISTS (
                            SELECT 1 FROM Poliza PZ
                            WHERE PZ.id_cliente = C.id
                              AND PZ.cancelada = false
                              AND PZ.inicio_vigencia <= CURRENT_TIMESTAMP
                              AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                        )
                    )
                '''))

            else:
                condiciones.append(sql.SQL('''
                    EXISTS (
                        SELECT 1 FROM ProcesoComercial PC2
                        WHERE PC2.id_prospecto = P.id
                          AND LOWER(PC2.codigo_estado_actual) = LOWER(%(filtro)s)
                    )
                '''))
                params["filtro"] = filtro

        if texto_busqueda:
            condiciones.append(sql.SQL('''
                (
                    LOWER(P.nombre_riesgo) LIKE LOWER(%(texto_busqueda)s)
                    OR LOWER(LN.nombre) LIKE LOWER(%(texto_busqueda)s)
                    OR LOWER(COALESCE(AC.nombre_administrador, '')) LIKE LOWER(%(texto_busqueda)s)
                    OR LOWER(COALESCE(EJ_COM.nombre, '')) LIKE LOWER(%(texto_busqueda)s)
                    OR LOWER(COALESCE(EI.nombre, '')) LIKE LOWER(%(texto_busqueda)s)
                    OR LOWER(COALESCE(EI.codigo, '')) LIKE LOWER(%(texto_busqueda)s)
                )
            '''))
            params["texto_busqueda"] = f"%{texto_busqueda}%"

        if region:
            condiciones.append(sql.SQL('LOWER(P.region) = LOWER(%(region)s)'))
            params["region"] = region

        if comuna:
            condiciones.append(sql.SQL('LOWER(P.comuna) = LOWER(%(comuna)s)'))
            params["comuna"] = comuna

        if condiciones:
            return sql.SQL(' AND ').join(condiciones)
        return sql.SQL('1=1')

    def _obtener_contadores(self, rut_usuario: Optional[str]) -> dict:
        contadores: dict = {}

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                params: dict = {}
                where_permisos = sql.SQL('')
                if rut_usuario:
                    where_permisos = sql.SQL('''
                        where (
                            P.rut_ej_comercial_asignado = %(rut_usuario)s
                            or P.rut_ej_evaluacion_asignado = %(rut_usuario)s
                            or C.rut_ej_renovacion_asignado = %(rut_usuario)s
                            or C.rut_ej_cobranza_asignado = %(rut_usuario)s
                        )
                    ''')
                    params["rut_usuario"] = rut_usuario

                query_estado_general = sql.SQL('''
                    select
                        CASE
                            WHEN C.id IS NULL THEN 'prospecto'
                            WHEN EXISTS (
                                SELECT 1 FROM Poliza PZ
                                WHERE PZ.id_cliente = C.id
                                  AND PZ.cancelada = false
                                  AND PZ.inicio_vigencia <= CURRENT_TIMESTAMP
                                  AND PZ.fin_vigencia > CURRENT_TIMESTAMP
                            ) THEN 'cliente_activo'
                            ELSE 'cliente_inactivo'
                        END as estado,
                        count(distinct P.id) as total
                    from Prospecto P
                    left join Cliente C
                    on P.id = C.id_prospecto
                    {where_permisos}
                    group by estado
                ''').format(where_permisos=where_permisos)
                cur.execute(query_estado_general, params)
                for row in cur.fetchall():
                    contadores[row['estado']] = row['total']

                if str(where_permisos):
                    where_comercial = sql.Composed([
                        where_permisos,
                        sql.SQL(' and (PC.codigo_estado_actual is not null)'),
                    ])
                else:
                    where_comercial = sql.SQL('where (PC.codigo_estado_actual is not null)')

                query_estado_comercial = sql.SQL('''
                    select PC.codigo_estado_actual as estado,
                           count(distinct P.id) as total
                    from Prospecto P
                    left join Cliente C
                    on P.id = C.id_prospecto
                    left join ProcesoComercial PC
                    on P.id = PC.id_prospecto
                    {where_comercial}
                    group by PC.codigo_estado_actual
                ''').format(where_comercial=where_comercial)
                cur.execute(query_estado_comercial, params)
                for row in cur.fetchall():
                    contadores[row['estado']] = row['total']

        return contadores

    def obtener_todos(
        self,
        rut_usuario: Optional[str] = None,
        filtro: Optional[str] = None,
        texto_busqueda: Optional[str] = None,
        pagina: int = 1,
        tamano_pagina: int = 25,
        region: Optional[str] = None,
        comuna: Optional[str] = None,
    ) -> dict:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                params: dict = {}
                where_condiciones = self._construir_where(filtro, texto_busqueda, rut_usuario, params, region, comuna)
                where_clause = sql.SQL('where {}').format(where_condiciones)

                filtrar_joins = self._filtrar_joins(texto_busqueda)

                count_query = sql.SQL('''
                    select count(distinct P.id) as total
                    from Prospecto P
                    {filtrar_joins}
                    {where_clause}
                ''').format(
                    filtrar_joins=filtrar_joins,
                    where_clause=where_clause,
                )
                cur.execute(count_query, params)
                total = cur.fetchone()['total'] # type: ignore

                total_paginas = math.ceil(total / tamano_pagina) if total else 0

                offset = (pagina - 1) * tamano_pagina

                page_query = sql.SQL('''
                    select distinct P.id, P.nombre_riesgo
                    from Prospecto P
                    {filtrar_joins}
                    {where_clause}
                    order by P.nombre_riesgo, P.id
                    limit %(tamano_pagina)s offset %(offset)s
                ''').format(
                    filtrar_joins=filtrar_joins,
                    where_clause=where_clause,
                )
                page_params = {**params, "tamano_pagina": tamano_pagina, "offset": offset}
                cur.execute(page_query, page_params)
                page_rows = cur.fetchall()

                prospectos: list[ProspectoResumen] = []

                if page_rows:
                    ids = [row['id'] for row in page_rows]

                    data_query = self._BASE_QUERY.format(
                        where_clause=sql.SQL('where P.id = ANY(%(ids)s)')
                    )
                    cur.execute(data_query, {"ids": ids})
                    rows = cur.fetchall()

                    if rows:
                        prospectos = DictRowsProspectoResumenAdapter(rows).to_prospectos_resumen()
                        prospectos.sort(key=lambda p: (p.nombre_riesgo, p.id))

                contadores = self._obtener_contadores(rut_usuario)

                return {
                    'data': prospectos,
                    'total': total,
                    'pagina': pagina,
                    'tamano_pagina': tamano_pagina,
                    'total_paginas': total_paginas,
                    'contadores_estado': contadores,
                }

    def obtener_por_administrador(
        self, id_administrador: int, rut_usuario: Optional[str] = None
    ) -> list[ProspectoResumen]:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                where_fragments: list[sql.Composable] = [
                    sql.SQL('where PCO.id_administrador = %(id_administrador)s')
                ]
                params: dict = {"id_administrador": id_administrador}

                if rut_usuario:
                    where_fragments.append(sql.SQL('''
                        and (P.rut_registrado_por = %(rut_usuario)s
                        or P.rut_ej_comercial_asignado = %(rut_usuario)s
                        or P.rut_ej_evaluacion_asignado = %(rut_usuario)s
                        or C.rut_ej_renovacion_asignado = %(rut_usuario)s)
                    '''))
                    params["rut_usuario"] = rut_usuario

                where_clause = sql.SQL(' ').join(where_fragments)

                query = self._BASE_QUERY.format(where_clause=where_clause)

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows:
                    return []

                return DictRowsProspectoResumenAdapter(rows).to_prospectos_resumen()