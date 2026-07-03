from psycopg.rows import DictRow

from app.dominio.cuota.cuota import Cuota
from app.dominio.plan_pago.plan_pago import PlanPago


class DictRowsPlanPagoAdapter:

    def __init__(self, rows: list[DictRow]) -> None:
        self.rows = rows

    def to_plan_pago(self) -> PlanPago:

        id = self.rows[0]['id']
        cuotas: list[Cuota] = []

        for row in self.rows:
            numero_cuota = row['numero_cuota']
            fecha_vencimiento = row['fecha_vencimiento']
            pagado = row['pagado']
            fecha_pago = row['fecha_pago']

            cuotas.append(Cuota(
                numero_cuota=numero_cuota,
                fecha_vencimiento=fecha_vencimiento,
                pagado=pagado,
                fecha_pago=fecha_pago
            ))

        return PlanPago(
            id=id,
            cuotas=cuotas
        )