from psycopg.rows import DictRow

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.dominio.poliza.poliza import Poliza


class DictRowPolizaAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_poliza(self) -> Poliza:
        company = None

        if self.row['id_company'] is not None:
            company = CompanySeguros(
                id=self.row['id_company'],
                nombre=self.row['company']
            )

        return Poliza(
            numero_poliza=self.row['numero_poliza'],
            nombre_cliente=self.row['nombre_cliente'],
            id_prospecto=self.row['id_prospecto'],
            id_proceso_comercial=self.row['id_proceso_comercial'],
            tipo=self.row['tipo'],
            nombre_producto=self.row['nombre_producto'],
            company=company,
            prima_neta=self.row['prima_neta'],
            comision_corredora_pct=self.row['comision_corredora_pct'],
            fecha_emision=self.row['fecha_emision'],
            inicio_vigencia=self.row['inicio_vigencia'],
            fin_vigencia=self.row['fin_vigencia'],
            estado=EstadoPoliza(self.row['estado']),
            renovacion_cotizada=self.row['renovacion_cotizada']
        )
