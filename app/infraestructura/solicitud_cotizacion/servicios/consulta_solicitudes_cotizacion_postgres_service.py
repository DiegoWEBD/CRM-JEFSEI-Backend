from psycopg import sql

from app.aplicacion.solicitud_cotizacion.dto.contadores_solicitudes_cotizacion import (
    ContadoresSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.filtro_solicitudes_cotizacion import (
    ESTADOS_SOLICITUDES,
    PRIORIDADES_SOLICITUDES,
    FiltroSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.solicitud_cotizacion_resumen import (
    SolicitudCotizacionResumen,
)
from app.aplicacion.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_service import (
    ConsultaSolicitudesCotizacionService,
)
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.solicitud_cotizacion.adaptadores.dictrow_solicitud_cotizacion_resumen_adapter import (
    DictRowSolicitudCotizacionResumenAdapter,
)


class ConsultaSolicitudesCotizacionPostgresService(ConsultaSolicitudesCotizacionService):

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
        inner join LineaNegocio LN
        on P.id_linea_negocio = LN.id
        left join ProspectoCondominio PCDO
        on P.id = PCDO.id
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

    # Definiciones de estado: las mismas que usan los contadores y el filtro.
    _CONDICIONES_ESTADO = {
        'informacion_incompleta': sql.SQL('not P.informacion_completa'),
        'listas_para_cotizar': sql.SQL('''
            P.informacion_completa
            and not exists(select 1 from Cotizacion C2 where C2.id_solicitud = SC.id)
        '''),
        'cotizaciones_emitidas': sql.SQL('''
            exists(select 1 from Cotizacion C2 where C2.id_solicitud = SC.id)
        '''),
        'estudios_emitidos': sql.SQL('''
            exists(select 1 from EstudioComercialCondominio E2 where E2.id_solicitud = SC.id)
        '''),
    }

    def listar(
        self,
        rut_scoping: str | None,
        filtro: FiltroSolicitudesCotizacion,
    ) -> tuple[list[SolicitudCotizacionResumen], int]:
        where_clause, params = self._construir_where(rut_scoping, filtro)

        consulta_total = sql.SQL('''
            select count(*) as total
            {from_clause}
            {where_clause}
        ''').format(from_clause=self._CLAUSULA_FROM, where_clause=where_clause)

        consulta_datos = sql.SQL('''
            select SC.id,
            P.nombre_riesgo,
            PC.id_prospecto,
            P.informacion_completa,
            EJ_COM.nombre as ejecutivo_comercial,
            SC.tipo,
            SC.recotizacion,
            SC.motivo_recotizacion,
            PR.nombre as producto,
            SC.prioridad,
            SC.fecha,
            exists(select 1 from EstudioComercialCondominio E where E.id_solicitud = SC.id) as estudio_disponible,
            exists(select 1 from Cotizacion C where C.id_solicitud = SC.id) as tiene_cotizaciones,
            LN.nombre as linea_negocio,
            P.rut_riesgo,
            P.telefono_contacto,
            P.correo_contacto,
            P.direccion,
            P.region,
            P.comuna,
            PCDO.id_administrador as administrador,
            PCDO.porcentaje_espacios_comunes,
            PCDO.tiene_locales_comerciales,
            PCDO.uso_del_condominio,
            PCDO.materialidad,
            PCDO.clasificacion_preliminar_incendio,
            PCDO.procesos_productivos,
            PCDO.numero_pisos,
            PCDO.numero_torres,
            PCDO.cantidad_departamentos,
            PCDO.cantidad_subterraneos,
            PCDO.tiene_piscina,
            PCDO.ubicacion_piscina,
            PCDO.tiene_alarma_incendio,
            PCDO.tiene_sprinklers,
            PCDO.year_construccion,
            PCDO.metros_cuadrados,
            PCDO.condominio_vertical
            {from_clause}
            {where_clause}
            order by SC.fecha desc
            limit %(tamano_pagina)s offset %(offset)s
        ''').format(from_clause=self._CLAUSULA_FROM, where_clause=where_clause)

        params_datos = {
            **params,
            'tamano_pagina': filtro.tamano_pagina,
            'offset': (filtro.pagina - 1) * filtro.tamano_pagina,
        }

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(consulta_total, params)
                total = cur.fetchone()['total'] # type: ignore

                cur.execute(consulta_datos, params_datos)
                rows = cur.fetchall()

        solicitudes = [
            DictRowSolicitudCotizacionResumenAdapter(row).to_solicitud_cotizacion_resumen()
            for row in rows
        ]
        return solicitudes, total

    def contadores(self, rut_scoping: str | None) -> ContadoresSolicitudesCotizacion:
        # Contadores globales: se calculan antes de los filtros de búsqueda y
        # paginación, solo respetan el scope por permisos.
        where_clause, params = self._construir_where(rut_scoping, None)

        consulta = sql.SQL('''
            select
            count(*) filter (where not P.informacion_completa) as informacion_incompleta,
            count(*) filter (
                where P.informacion_completa
                and not exists(select 1 from Cotizacion C where C.id_solicitud = SC.id)
            ) as listas_para_cotizar,
            count(*) filter (
                where exists(select 1 from Cotizacion C where C.id_solicitud = SC.id)
            ) as cotizaciones_emitidas,
            count(*) filter (
                where exists(select 1 from EstudioComercialCondominio E where E.id_solicitud = SC.id)
            ) as estudios_emitidos
            {from_clause}
            {where_clause}
        ''').format(from_clause=self._CLAUSULA_FROM, where_clause=where_clause)

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(consulta, params)
                row = cur.fetchone()

                return ContadoresSolicitudesCotizacion(
                    informacion_incompleta=row['informacion_incompleta'] if row else 0,
                    listas_para_cotizar=row['listas_para_cotizar'] if row else 0,
                    cotizaciones_emitidas=row['cotizaciones_emitidas'] if row else 0,
                    estudios_emitidos=row['estudios_emitidos'] if row else 0,
                )

    def _construir_where(
        self,
        rut_scoping: str | None,
        filtro: FiltroSolicitudesCotizacion | None,
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
            condiciones.append(self._CONDICIONES_ESTADO[filtro.estado])

        if filtro is not None and filtro.prioridad is not None:
            condiciones.append(sql.SQL(
                'unaccent(lower(SC.prioridad)) = unaccent(lower(%(prioridad)s))'
            ))
            params['prioridad'] = filtro.prioridad

        # El RUT se compara exacto: no se le aplica unaccent ni lower.
        if filtro is not None and filtro.rut_usuario is not None:
            condiciones.append(sql.SQL('PC.rut_ej_comercial = %(rut_usuario)s'))
            params['rut_usuario'] = filtro.rut_usuario

        where_clause = sql.SQL(' WHERE ') + sql.SQL(' AND ').join(condiciones)
        return where_clause, params

    @staticmethod
    def _validar_filtro(filtro: FiltroSolicitudesCotizacion) -> None:
        if filtro.estado is not None and filtro.estado not in ESTADOS_SOLICITUDES:
            raise ValueError(f'Estado inválido: {filtro.estado}')

        if filtro.prioridad is not None and filtro.prioridad not in PRIORIDADES_SOLICITUDES:
            raise ValueError(f'Prioridad inválida: {filtro.prioridad}')

    @staticmethod
    def _escapar_comodines(texto: str) -> str:
        return texto.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
