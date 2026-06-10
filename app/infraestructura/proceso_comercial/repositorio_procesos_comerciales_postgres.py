from app.dominio.proceso_comercial.proceso_comercial import ProcesoComercial
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.proceso_comercial.adaptadores.dictrow_proceso_comercial_adapter import DictRowProcesoComercialAdapter


class RepositorioProcesosComercialesPostgres(RepositorioProcesosComerciales):

    def obtener_procesos_comerciales(self, id_prospecto: int) -> list[ProcesoComercial]:
         with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PC.id,
                    PC.codigo_etapa_actual,
                    PC.cerrado,
                    PC.rut_ej_comercial,
                    EJ_COM.nombre as nombre_ej_comercial,
                    PC.rut_ej_evaluacion,
                    EJ_EV.nombre as nombre_ej_evaluacion,
                    PC.id_producto, 
                    P.nombre as nombre_producto
                    from ProcesoComercial PC
                    inner join Producto P
                    on PC.id_producto = P.id
                    left join Usuario EJ_COM
                    on PC.rut_ej_comercial = EJ_COM.rut
                    left join Usuario EJ_EV
                    on PC.rut_ej_evaluacion = EJ_EV.rut
                    where PC.id_prospecto = %(id_prospecto)s
                '''

                params = {
                    'id_prospecto': id_prospecto
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                return [DictRowProcesoComercialAdapter(row).to_proceso_comercial() for row in rows]