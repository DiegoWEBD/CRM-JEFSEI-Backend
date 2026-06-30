from app.dominio.plan_pago.plan_pago import PlanPago
from app.dominio.plan_pago.repositorio_planes_pago import RepositorioPlanesPago
from app.dominio.poliza.poliza import Poliza
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
            
    def registrar_plan_pago_poliza(self, poliza: Poliza, plan_pago: PlanPago, rut_usuario: str) -> None:
        ESTADO_PLAN_PAGO_CREADO = 'PLAN_PAGO_CREADO'

        with obtener_conexion() as conn:
            with conn.cursor() as cur:

                query = '''
                    insert into PlanPago (numero_poliza)
                    values (%(numero_poliza)s)
                    returning id
                '''

                params = {
                    'numero_poliza': poliza.numero_poliza
                }

                cur.execute(query, params)
                row = cur.fetchone()

                id_plan = row['id'] # type: ignore

                for cuota in plan_pago.cuotas:
                    query = '''
                        insert into Cuota (id_plan_pago, numero_cuota, fecha_vencimiento, pagado, fecha_pago)
                        values (%(id_plan_pago)s, %(numero_cuota)s, %(fecha_vencimiento)s, %(pagado)s, %(fecha_pago)s)
                    '''

                    params = {
                        'id_plan_pago': id_plan,
                        'numero_cuota': cuota.numero_cuota,
                        'fecha_vencimiento': cuota.fecha_vencimiento,
                        'pagado': cuota.pagado,
                        'fecha_pago': cuota.fecha_pago
                    }

                    cur.execute(query, params)

                # Registro de historial

                query = '''
                    insert into HistorialEstadoInformativoProcesoComercial (
                        id_proceso_comercial,
                        codigo_estado,
                        rut_registrado_por
                    )
                    select
                        %(id_proceso_comercial)s,
                        %(codigo_estado)s,
                        %(rut_registrado_por)s
                    where coalesce(
                        (
                            select codigo_estado
                            from HistorialEstadoInformativoProcesoComercial
                            where id_proceso_comercial = %(id_proceso_comercial)s
                            order by fecha_registro desc
                            limit 1
                        ),
                        ''
                    ) <> %(codigo_estado)s
                '''

                params = {
                    'id_proceso_comercial': poliza.id_proceso_comercial,
                    'codigo_estado': ESTADO_PLAN_PAGO_CREADO,
                    'rut_registrado_por': rut_usuario
                }

                cur.execute(query, params)