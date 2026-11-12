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


_CLAUSULA_FROM = '''
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
'''

# El scope por permisos: sin scoping se ve todo, con scoping solo las
# solicitudes asignadas al usuario en el prospecto base.
_CLAUSULA_SCOPE = '''
    where not PC.cerrado
    and (
        cast(%(rut_scoping)s as varchar) is null
        or P.rut_ej_comercial_asignado = %(rut_scoping)s
        or P.rut_ej_evaluacion_asignado = %(rut_scoping)s
    )
'''

# Definiciones de estado: las mismas que usan los contadores y el filtro.
_CONDICIONES_ESTADO = {
    'informacion_incompleta': '''
        and not P.informacion_completa
    ''',
    'listas_para_cotizar': '''
        and P.informacion_completa
        and not exists(select 1 from Cotizacion C2 where C2.id_solicitud = SC.id)
    ''',
    'cotizaciones_emitidas': '''
        and exists(select 1 from Cotizacion C2 where C2.id_solicitud = SC.id)
    ''',
    'estudios_emitidos': '''
        and exists(select 1 from EstudioComercialCondominio E2 where E2.id_solicitud = SC.id)
    ''',
}


class ConsultaSolicitudesCotizacionPostgresService(ConsultaSolicitudesCotizacionService):

    def listar(
        self,
        rut_scoping: str | None,
        filtro: FiltroSolicitudesCotizacion,
    ) -> tuple[list[SolicitudCotizacionResumen], int]:
        condiciones, params = self._condiciones_de_filtro(rut_scoping, filtro)

        consulta_total = f'''
            select count(*) as total
            {_CLAUSULA_FROM}
            {_CLAUSULA_SCOPE}
            {condiciones}
        '''

        consulta_datos = f'''
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
            exists(select 1 from Cotizacion C where C.id_solicitud = SC.id) as tiene_cotizaciones
            {_CLAUSULA_FROM}
            {_CLAUSULA_SCOPE}
            {condiciones}
            order by SC.fecha desc
            limit %(tamano_pagina)s offset %(offset)s
        '''

        params_datos = {
            **params,
            'tamano_pagina': filtro.tamano_pagina,
            'offset': (filtro.pagina - 1) * filtro.tamano_pagina,
        }

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(consulta_total, params)
                total = cur.fetchone()['total']

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
        consulta = f'''
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
            {_CLAUSULA_FROM}
            {_CLAUSULA_SCOPE}
        '''
        params = {'rut_scoping': rut_scoping}

        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(consulta, params)
                row = cur.fetchone()

        return ContadoresSolicitudesCotizacion(
            informacion_incompleta=row['informacion_incompleta'],
            listas_para_cotizar=row['listas_para_cotizar'],
            cotizaciones_emitidas=row['cotizaciones_emitidas'],
            estudios_emitidos=row['estudios_emitidos'],
        )

    def _condiciones_de_filtro(
        self,
        rut_scoping: str | None,
        filtro: FiltroSolicitudesCotizacion,
    ) -> tuple[str, dict]:
        if filtro.estado is not None and filtro.estado not in ESTADOS_SOLICITUDES:
            raise ValueError(f'Estado inválido: {filtro.estado}')

        if filtro.prioridad is not None and filtro.prioridad not in PRIORIDADES_SOLICITUDES:
            raise ValueError(f'Prioridad inválida: {filtro.prioridad}')

        condiciones = []
        params = {'rut_scoping': rut_scoping}

        if filtro.texto_busqueda:
            condiciones.append('''
                and (
                    unaccent(lower(P.nombre_riesgo)) like unaccent(lower(%(texto_busqueda)s)) escape '\\'
                    or unaccent(lower(PR.nombre)) like unaccent(lower(%(texto_busqueda)s)) escape '\\'
                    or unaccent(lower(EJ_COM.nombre)) like unaccent(lower(%(texto_busqueda)s)) escape '\\'
                )
            ''')
            patron = self._escapar_comodines(filtro.texto_busqueda.lower())
            params['texto_busqueda'] = f'%{patron}%'

        if filtro.estado is not None:
            condiciones.append(_CONDICIONES_ESTADO[filtro.estado])

        if filtro.prioridad is not None:
            condiciones.append(
                'and unaccent(lower(SC.prioridad)) = unaccent(lower(%(prioridad)s))'
            )
            params['prioridad'] = filtro.prioridad

        # El RUT se compara exacto: no se le aplica unaccent ni lower.
        if filtro.rut_usuario is not None:
            condiciones.append('and PC.rut_ej_comercial = %(rut_usuario)s')
            params['rut_usuario'] = filtro.rut_usuario

        return '\n'.join(condiciones), params

    @staticmethod
    def _escapar_comodines(texto: str) -> str:
        return texto.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
