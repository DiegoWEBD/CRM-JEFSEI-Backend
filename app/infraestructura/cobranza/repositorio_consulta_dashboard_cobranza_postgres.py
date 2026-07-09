from datetime import date

from app.dominio.cobranza.repositorio_consulta_dashboard_cobranza import (
    RepositorioConsultaDashboardCobranza,
)
from app.infraestructura.db.conexion import obtener_conexion


class RepositorioConsultaDashboardCobranzaPostgres(
    RepositorioConsultaDashboardCobranza
):

    def obtener_cuotas_dashboard(self, rut_usuario: str) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    select
                        CU.id as cuota_id,
                        CU.numero_cuota,
                        CU.fecha_vencimiento,
                        CU.pagado,
                        CU.fecha_pago,
                        PP.id as id_plan_pago,
                        PP.numero_poliza,
                        PR.nombre as producto,
                        CS.nombre as compania,
                        C.id_prospecto,
                        P.nombre_riesgo as nombre_cliente,
                        P.rut_riesgo,
                        P.telefono_contacto,
                        count(*) over (partition by PP.id) as total_cuotas
                    from Cuota CU
                    inner join PlanPago PP
                        on CU.id_plan_pago = PP.id
                    inner join Poliza POL
                        on PP.numero_poliza = POL.numero_poliza
                    left join ProcesoComercial PC
                        on POL.id_proceso_comercial = PC.id
                    left join Producto PR
                        on PC.id_producto = PR.id
                    left join CompanySeguros CS
                        on POL.id_company = CS.id
                    inner join Cliente C
                        on POL.id_cliente = C.id
                    inner join Prospecto P
                        on C.id_prospecto = P.id
                    where C.rut_ej_cobranza_asignado = %(rut_usuario)s
                      and POL.cancelada = false
                    order by P.nombre_riesgo, PP.numero_poliza, CU.numero_cuota
                """
                cur.execute(query, {"rut_usuario": rut_usuario})
                return cur.fetchall()

    def obtener_polizas_sin_plan_pago(self, rut_usuario: str) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    select
                        POL.numero_poliza,
                        C.id_prospecto,
                        P.nombre_riesgo as nombre_cliente,
                        P.rut_riesgo,
                        P.telefono_contacto,
                        PR.nombre as producto,
                        CS.nombre as compania,
                        POL.cancelada
                    from Poliza POL
                    inner join Cliente C
                        on POL.id_cliente = C.id
                    inner join Prospecto P
                        on C.id_prospecto = P.id
                    left join ProcesoComercial PC
                        on POL.id_proceso_comercial = PC.id
                    left join Producto PR
                        on PC.id_producto = PR.id
                    left join CompanySeguros CS
                        on POL.id_company = CS.id
                    where C.rut_ej_cobranza_asignado = %(rut_usuario)s
                      and POL.cancelada = false
                      and not exists (
                          select 1 from PlanPago PP
                          where PP.numero_poliza = POL.numero_poliza
                      )
                    order by P.nombre_riesgo, POL.numero_poliza
                """
                cur.execute(query, {"rut_usuario": rut_usuario})
                return cur.fetchall()

    def obtener_recordatorios_cobranza(
        self, rut_usuario: str, fecha_hasta: date
    ) -> list[dict]:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                query = """
                    select
                        R.id as id_recordatorio,
                        R.fecha_recordatorio,
                        CU.id as cuota_id,
                        C.id_prospecto
                    from Recordatorio R
                    inner join RecordatorioCobranzaCuotaPoliza RCCP
                        on R.id = RCCP.id
                    inner join Cuota CU
                        on RCCP.id_cuota = CU.id
                    inner join PlanPago PP
                        on CU.id_plan_pago = PP.id
                    inner join Poliza POL
                        on PP.numero_poliza = POL.numero_poliza
                    inner join Cliente C
                        on POL.id_cliente = C.id
                    where C.rut_ej_cobranza_asignado = %(rut_usuario)s
                      and POL.cancelada = false
                      and R.completado = false
                      and R.fecha_recordatorio::date <= %(fecha_hasta)s
                    order by R.fecha_recordatorio
                """
                cur.execute(
                    query,
                    {
                        "rut_usuario": rut_usuario,
                        "fecha_hasta": fecha_hasta.isoformat(),
                    },
                )
                return cur.fetchall()
