from datetime import datetime, timezone

from psycopg import sql

from app.aplicacion.solicitud_cotizacion.dto.contadores_panel_cotizaciones import (
    ContadoresPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.dto.filtro_panel_cotizaciones import (
    ESTADOS_PANEL_COTIZACIONES,
    PRIORIDADES_PANEL_COTIZACIONES,
    FiltroPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.dto.fila_panel_cotizaciones import (
    FilaPanelCotizaciones,
)
from app.aplicacion.solicitud_cotizacion.servicios.consulta_panel_cotizaciones_service import (
    ConsultaPanelCotizacionesService,
)
from app.dominio.cotizacion.servicio_estado_cotizacion import (
    INTERVALO_VENCIMIENTO_DIAS,
)
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.solicitud_cotizacion.adaptadores.dictrow_fila_panel_cotizaciones_adapter import (
    DictRowFilaPanelCotizacionesAdapter,
)


class ConsultaPanelCotizacionesPostgresService(ConsultaPanelCotizacionesService):
    """
    Listado del panel de cotizaciones y estudios: una fila por solicitud de
    cotización con el resumen de sus cotizaciones embebido (sin N+1) y los
    contadores globales calculados antes de aplicar cualquier filtro.
    """

    _CLAUSULA_FROM = sql.SQL('''
        from SolicitudCotizacion SC
        inner join ProcesoComercial PC
        on SC.id_proceso_comercial = PC.id
        inner join Producto PR
        on PC.id_producto = PR.id
        and PR.eliminado = false
        inner join Usuario EJ_COM
        on PC.rut_ej_comercial = EJ_COM.rut
        inner join Prospecto P
        on PC.id_prospecto = P.id
    ''')

    # El scope por permisos: sin scoping se ve todo, con scoping solo las
    # solicitudes asignadas al usuario en el prospecto base.
    _CONDICION_SCOPE = sql.SQL('''
        not PC.cerrado
        and (
            cast(%(rut_scoping)s as varchar) is null
            or P.rut_ej_comercial_asignado = %(rut_scoping)s
            or P.rut_ej_evaluacion_asignado = %(rut_scoping)s
        )
    ''')

    # Agregado liviano de cotizaciones por solicitud. Los `array_agg` ordenados
    # por vencimiento traen las fechas de la cotización más próxima a vencer
    # (la que define el estado de la fila, igual que en el panel actual).
    _LATERAL_COTIZACIONES_SLIM = sql.SQL('''
        left join lateral (
            select
            count(*) as cantidad,
            (array_agg(C.fecha_emision order by C.fecha_vencimiento asc))[1] as cot_emision,
            (array_agg(C.fecha_vencimiento order by C.fecha_vencimiento asc))[1] as cot_vencimiento
            from Cotizacion C
            where C.id_solicitud = SC.id
        ) COT on true
    ''')

    @classmethod
    def _lateral_cotizaciones(cls) -> sql.Composable:
        # Mismo agregado que el slim, más el resumen de cada cotización en un
        # solo json_agg: toda la info del panel viaja en la query de la página.
        return sql.SQL('''
            left join lateral (
                select
                count(*) as cantidad,
                (array_agg(C.fecha_emision order by C.fecha_vencimiento asc))[1] as cot_emision,
                (array_agg(C.fecha_vencimiento order by C.fecha_vencimiento asc))[1] as cot_vencimiento,
                json_agg(
                    json_build_object(
                        'id', C.id,
                        'company', CS.nombre,
                        'prima_neta', C.prima_neta,
                        'prima_bruta', C.prima_bruta,
                        'fecha_vencimiento', C.fecha_vencimiento,
                        'estado', {estado_cotizacion}
                    )
                    order by C.fecha_vencimiento asc
                ) as cotizaciones
                from Cotizacion C
                inner join CompanySeguros CS
                on CS.id = C.id_company
                where C.id_solicitud = SC.id
            ) COT on true
        ''').format(estado_cotizacion=cls._estado_cotizacion('C'))

    @staticmethod
    def _estado_cotizacion(alias: str) -> sql.Composable:
        """
        CASE con la misma clasificación que calcular_estado_cotizacion()
        (el piso en segundos replica exactamente timedelta.days de Python).

        El alias de la tabla se emite sin citar a propósito: los alias del
        lateral (p. ej. `from Cotizacion C`) se pliegan a minúsculas en
        Postgres, y un identificador citado como "C" no coincidiría con ellos.
        """
        emision = sql.SQL('{}.{}').format(
            sql.SQL(alias), sql.Identifier('fecha_emision') # type: ignore
        )
        vencimiento = sql.SQL('{}.{}').format(
            sql.SQL(alias), sql.Identifier('fecha_vencimiento') # type: ignore
        )
        return sql.SQL('''
            case
                when {emision} > %(ahora)s then 'REGISTRADA'
                when {vencimiento} > %(ahora)s
                    and floor(extract(epoch from ({vencimiento} - %(ahora)s)) / 86400) <= %(intervalo_vencimiento)s
                then 'POR_VENCER'
                when {vencimiento} > %(ahora)s then 'VIGENTE'
                else 'VENCIDA'
            end
        ''').format(emision=emision, vencimiento=vencimiento)

    @staticmethod
    def _estado_fila() -> sql.Composable:
        # Estado de la fila = estado de la cotización de vencimiento más
        # próximo. Sin cotizaciones con vencimiento, la fila no tiene estado.
        return sql.SQL('''
            case
                when COT.cot_vencimiento is null then null
                when COT.cot_emision > %(ahora)s then 'REGISTRADA'
                when COT.cot_vencimiento > %(ahora)s
                    and floor(extract(epoch from (COT.cot_vencimiento - %(ahora)s)) / 86400) <= %(intervalo_vencimiento)s
                then 'POR_VENCER'
                when COT.cot_vencimiento > %(ahora)s then 'VIGENTE'
                else 'VENCIDA'
            end
        ''')

    @classmethod
    def _condicion_estado(cls, estado: str) -> sql.Composable:
        if estado == 'estudios_pendientes':
            return sql.SQL(
                'not exists(select 1 from EstudioComercialCondominio E where E.id_solicitud = SC.id)'
            )

        if estado == 'estudios_emitidos':
            return sql.SQL(
                'exists(select 1 from EstudioComercialCondominio E where E.id_solicitud = SC.id)'
            )

        estado_cotizacion = {
            'cotizaciones_vigentes': 'VIGENTE',
            'cotizaciones_por_vencer': 'POR_VENCER',
            'cotizaciones_vencidas': 'VENCIDA',
        }[estado]
        return sql.SQL('({} = {})').format(
            cls._estado_fila(), sql.Literal(estado_cotizacion)
        )

    def listar(
        self,
        rut_scoping: str | None,
        filtro: FiltroPanelCotizaciones,
    ) -> tuple[list[FilaPanelCotizaciones], int]:
        where_clause, params = self._construir_where(rut_scoping, filtro)

        consulta_total = sql.SQL('''
            select count(*) as total
            {from_clause}
            {lateral}
            {where_clause}
        ''').format(
            from_clause=self._CLAUSULA_FROM,
            lateral=self._LATERAL_COTIZACIONES_SLIM,
            where_clause=where_clause,
        )

        consulta_datos = sql.SQL('''
            select
            SC.id,
            PC.id_prospecto,
            PC.id as id_proceso_comercial,
            P.nombre_riesgo as cliente,
            PR.nombre as linea_seguro,
            EJ_COM.nombre as ejecutivo_comercial,
            SC.prioridad,
            SC.fecha,
            COT.cantidad as cantidad_cotizaciones,
            COT.cot_vencimiento as vencimiento_mas_proximo,
            {estado_fila} as estado,
            exists(select 1 from EstudioComercialCondominio E where E.id_solicitud = SC.id) as tiene_estudio,
            (select max(E.id) from EstudioComercialCondominio E where E.id_solicitud = SC.id) as id_estudio,
            coalesce(COT.cotizaciones, '[]'::json) as cotizaciones
            {from_clause}
            {lateral}
            {where_clause}
            order by SC.fecha desc
            limit %(tamano_pagina)s offset %(offset)s
        ''').format(
            estado_fila=self._estado_fila(),
            from_clause=self._CLAUSULA_FROM,
            lateral=self._lateral_cotizaciones(),
            where_clause=where_clause,
        )

        params_comunes = {**params, **self._params_tiempo()}
        params_datos = {
            **params_comunes,
            'tamano_pagina': filtro.tamano_pagina,
            'offset': (filtro.pagina - 1) * filtro.tamano_pagina,
        }

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(consulta_total, params_comunes)
                total = cur.fetchone()['total']  # type: ignore

                cur.execute(consulta_datos, params_datos)
                rows = cur.fetchall()

        filas = [
            DictRowFilaPanelCotizacionesAdapter(row).to_fila_panel_cotizaciones()
            for row in rows
        ]
        return filas, total

    def contadores(self, rut_scoping: str | None) -> ContadoresPanelCotizaciones:
        # Contadores globales: se calculan antes de los filtros de búsqueda,
        # estado, prioridad y ejecutivo; solo respetan el scope por permisos.
        where_clause, params = self._construir_where(rut_scoping, None)

        consulta = sql.SQL('''
            select
            count(*) filter (where {estado_fila} = 'VIGENTE') as cotizaciones_vigentes,
            count(*) filter (where {estado_fila} = 'POR_VENCER') as cotizaciones_por_vencer,
            count(*) filter (where {estado_fila} = 'VENCIDA') as cotizaciones_vencidas,
            count(*) filter (
                where not exists(select 1 from EstudioComercialCondominio E where E.id_solicitud = SC.id)
            ) as estudios_pendientes,
            count(*) filter (
                where exists(select 1 from EstudioComercialCondominio E where E.id_solicitud = SC.id)
            ) as estudios_emitidos
            {from_clause}
            {lateral}
            {where_clause}
        ''').format(
            estado_fila=self._estado_fila(),
            from_clause=self._CLAUSULA_FROM,
            lateral=self._LATERAL_COTIZACIONES_SLIM,
            where_clause=where_clause,
        )

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(consulta, {**params, **self._params_tiempo()})
                row = cur.fetchone()

                return ContadoresPanelCotizaciones(
                    cotizaciones_vigentes=row['cotizaciones_vigentes'] if row else 0,
                    cotizaciones_por_vencer=row['cotizaciones_por_vencer'] if row else 0,
                    cotizaciones_vencidas=row['cotizaciones_vencidas'] if row else 0,
                    estudios_pendientes=row['estudios_pendientes'] if row else 0,
                    estudios_emitidos=row['estudios_emitidos'] if row else 0,
                )

    @staticmethod
    def _params_tiempo() -> dict:
        # Un único "ahora" por request para que datos, filtros y contadores
        # clasifiquen los estados exactamente igual.
        return {
            'ahora': datetime.now(tz=timezone.utc),
            'intervalo_vencimiento': INTERVALO_VENCIMIENTO_DIAS,
        }

    def _construir_where(
        self,
        rut_scoping: str | None,
        filtro: FiltroPanelCotizaciones | None,
    ) -> tuple[sql.Composable, dict]:
        if filtro is not None:
            self._validar_filtro(filtro)

        condiciones: list[sql.Composable] = [self._CONDICION_SCOPE]
        params: dict = {'rut_scoping': rut_scoping}

        if filtro is not None and filtro.texto_busqueda:
            condiciones.append(sql.SQL('''
                (
                    unaccent(lower(P.nombre_riesgo)) like unaccent(lower(%(texto_busqueda)s)) escape '\\'
                    or unaccent(lower(PR.nombre)) like unaccent(lower(%(texto_busqueda)s)) escape '\\'
                    or unaccent(lower(EJ_COM.nombre)) like unaccent(lower(%(texto_busqueda)s)) escape '\\'
                )
            '''))
            patron = self._escapar_comodines(filtro.texto_busqueda.lower())
            params['texto_busqueda'] = f'%{patron}%'

        if filtro is not None and filtro.estado is not None:
            condiciones.append(self._condicion_estado(filtro.estado))

        if filtro is not None and filtro.prioridad is not None:
            condiciones.append(sql.SQL(
                'unaccent(lower(SC.prioridad)) = unaccent(lower(%(prioridad)s))'
            ))
            params['prioridad'] = filtro.prioridad

        # El RUT se compara exacto: no se le aplica unaccent ni lower.
        if filtro is not None and filtro.rut_ejecutivo is not None:
            condiciones.append(sql.SQL('PC.rut_ej_comercial = %(rut_ejecutivo)s'))
            params['rut_ejecutivo'] = filtro.rut_ejecutivo

        where_clause = sql.SQL(' WHERE ') + sql.SQL(' AND ').join(condiciones)
        return where_clause, params

    @staticmethod
    def _validar_filtro(filtro: FiltroPanelCotizaciones) -> None:
        if filtro.estado is not None and filtro.estado not in ESTADOS_PANEL_COTIZACIONES:
            raise ValueError(f'Estado inválido: {filtro.estado}')

        if (
            filtro.prioridad is not None
            and filtro.prioridad not in PRIORIDADES_PANEL_COTIZACIONES
        ):
            raise ValueError(f'Prioridad inválida: {filtro.prioridad}')

    @staticmethod
    def _escapar_comodines(texto: str) -> str:
        return texto.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
