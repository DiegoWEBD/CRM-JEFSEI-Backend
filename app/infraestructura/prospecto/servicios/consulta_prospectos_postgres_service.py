from typing import Optional

from app.aplicacion.prospecto.dto.prospecto_resumen import ProspectoResumen
from app.aplicacion.prospecto.servicios.consulta_prospectos_service import ConsultaProspectosService
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.prospecto.adaptadores.dictrows_prospectos_resumen_adapter import DictRowsProspectoResumenAdapter


class ConsultaProspectosPostgresService(ConsultaProspectosService):

    _BASE_QUERY = '''
        select distinct on (P.nombre_riesgo, PC.id) 
        P.id,
        PC.id as id_proceso_comercial,
        C.id as id_cliente,
        P.nombre_riesgo,
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
        on PC.rut_ej_comercial = EJ_COM.rut
        {where_clause}
        order by P.nombre_riesgo, PC.id, HE.fecha_registro desc
    '''

    def obtener_todos(self, rut_usuario: Optional[str] = None) -> list[ProspectoResumen]:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                params = {}
                where_clause = ""

                if rut_usuario:

                    where_clause = '''
                        where P.rut_ej_comercial_asignado = %(rut_usuario)s
                        or P.rut_ej_evaluacion_asignado = %(rut_usuario)s
                        or C.rut_ej_renovacion_asignado = %(rut_usuario)s
                        or C.rut_ej_cobranza_asignado = %(rut_usuario)s
                    '''

                    params["rut_usuario"] = rut_usuario

                query = self._BASE_QUERY.format(
                    where_clause=where_clause
                )

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows:
                    return []

                return DictRowsProspectoResumenAdapter(rows).to_prospectos_resumen()

    def obtener_por_administrador(
        self, id_administrador: int, rut_usuario: Optional[str] = None
    ) -> list[ProspectoResumen]:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                where_clause = "where PCO.id_administrador = %(id_administrador)s"
                params: dict = {"id_administrador": id_administrador}

                if rut_usuario:
                    where_clause += '''
                        and (P.rut_registrado_por = %(rut_usuario)s
                        or P.rut_ej_comercial_asignado = %(rut_usuario)s
                        or P.rut_ej_evaluacion_asignado = %(rut_usuario)s
                        or C.rut_ej_renovacion_asignado = %(rut_usuario)s)
                    '''
                    params["rut_usuario"] = rut_usuario

                query = self._BASE_QUERY.format(
                    where_clause=where_clause
                )

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows:
                    return []

                return DictRowsProspectoResumenAdapter(rows).to_prospectos_resumen()
        