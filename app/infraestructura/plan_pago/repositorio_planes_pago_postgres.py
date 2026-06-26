from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago
from app.infraestructura.db.conexion import obtener_conexion
from app.infraestructura.plan_pago.adaptadores.dictrows_plan_pago_adapter import DictRowsPlanPagoAdapter


class RepositorioPlanesPagoPostgres(RepositorioPlanesPago):

    def buscar_plan_pago_poliza(self, numero_poliza: str) -> PlanPago | None:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    select PP.id,
                    C.numero_cuota,
                    C.fecha_vencimiento,
                    C.pagado,
                    C.fecha_pago
                    from PlanPago PP
                    inner join Cuota C
                    on PP.id = C.id_plan_pago
                    where PP.numero_poliza = %(numero_poliza)s
                '''

                params = {
                    'numero_poliza': numero_poliza
                }

                cur.execute(query, params)
                rows = cur.fetchall()

                if len(rows) == 0:
                    return None

                return DictRowsPlanPagoAdapter(rows).to_plan_pago()