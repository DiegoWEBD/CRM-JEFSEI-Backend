from typing import Optional

from app.aplicacion.prospecto.dto.prospecto_resumen import ProspectoResumen
from app.aplicacion.prospecto.servicios.consulta_prospectos_service import ConsultaProspectosService
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.prospecto.adaptadores.tuplerow_prospecto_resumen_adapter import TupleRowProspectoResumenAdapter


class ConsultaProspectosPostgresService(ConsultaProspectosService):

    def obtener_todos(self, rut_usuario: Optional[str] = None) -> list[ProspectoResumen]:

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                base_query = '''
                    select distinct on (P.id)
                    P.nombre_riesgo,
                    P.nombre_contacto,
                    LN.nombre as linea_negocio,
                    EB.nombre as estado,
                    HE.fecha_registro as fecha_ultima_accion,
                    EB2.nombre as proxima_accion
                    {extra_fields}
                    from Prospecto P
                    inner join LineaNegocio LN on P.id_linea_negocio = LN.id
                    inner join ProcesoComercial PC on P.id = PC.id_prospecto
                    inner join HistorialEstado HE on PC.id = HE.id_proceso_comercial
                    inner join EstadoParticular EP on HE.id_estado_particular = EP.id
                    inner join EstadoBase EB on EP.codigo_estado_base = EB.codigo
                    left join EstadoBase EB2 on EB.codigo_siguiente_estado = EB2.codigo
                    {extra_joins}
                    {where_clause}
                    order by P.id, HE.fecha_registro desc
                '''

                params = {}
                extra_fields = ""
                extra_joins = ""
                where_clause = ""

                if rut_usuario:
                    extra_fields = '''
                        ,P.rut_registrado_por,
                        ER.rut_ej_comercial,
                        ER.rut_ej_evaluacion
                    '''

                    extra_joins = '''
                        left join EvaluacionRiesgo ER
                        on PC.id = ER.id_proceso_comercial
                    '''

                    where_clause = '''
                        where P.rut_registrado_por = %(rut_usuario)s
                        or ER.rut_ej_comercial = %(rut_usuario)s
                        or ER.rut_ej_evaluacion = %(rut_usuario)s
                    '''

                    params["rut_usuario"] = rut_usuario

                query = base_query.format(
                    extra_fields=extra_fields,
                    extra_joins=extra_joins,
                    where_clause=where_clause
                )

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows:
                    return []

                return [TupleRowProspectoResumenAdapter(row) for row in rows]