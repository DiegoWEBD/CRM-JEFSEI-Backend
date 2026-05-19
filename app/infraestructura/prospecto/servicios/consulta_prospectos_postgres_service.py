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
                    P.id,
                    P.nombre_riesgo,
                    P.nombre_contacto,
                    LN.nombre as linea_negocio,
                    EB.nombre as estado,
                    EB.color as color_estado,
                    EB.dias_limite as dias_limite_base,
                    EP.dias_limite_particular,
                    HE.fecha_registro as fecha_ultima_accion,
                    extract(day from (now() - HE.fecha_registro)) AS dias_transcurridos,
                    EB2.nombre as proxima_accion
                    from Prospecto P
                    inner join LineaNegocio LN on P.id_linea_negocio = LN.id
                    inner join ProcesoComercial PC on P.id = PC.id_prospecto
                    inner join HistorialEstado HE on PC.id = HE.id_proceso_comercial
                    inner join EstadoParticular EP on HE.id_estado_particular_actual = EP.id
                    inner join EstadoBase EB on EP.codigo_estado_base = EB.codigo
                    left join EstadoBase EB2 on EB.codigo_siguiente_estado = EB2.codigo
                    {where_clause}
                    order by P.id, HE.fecha_registro desc
                '''

                params = {}
                where_clause = ""

                if rut_usuario:

                    where_clause = '''
                        where P.rut_registrado_por = %(rut_usuario)s
                        or PC.rut_ej_comercial = %(rut_usuario)s
                        or PC.rut_ej_evaluacion = %(rut_usuario)s
                    '''

                    params["rut_usuario"] = rut_usuario

                query = base_query.format(
                    where_clause=where_clause
                )

                cur.execute(query, params)
                rows = cur.fetchall()

                if not rows:
                    return []

                return [TupleRowProspectoResumenAdapter(row) for row in rows]
        