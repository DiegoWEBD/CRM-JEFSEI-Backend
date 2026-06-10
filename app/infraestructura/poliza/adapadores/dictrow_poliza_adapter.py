from psycopg.rows import DictRow

from app.dominio.poliza.poliza import Poliza


class DictRowPolizaAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_poliza(self) -> Poliza:
        
        return Poliza(
            numero_poliza=self.row['numero_poliza'],
            tipo=self.row['tipo'],
            company=self.row['company'],
            prima_neta=self.row['prima_neta'],
            comision_corredora_pct=self.row['comision_corredora_pct'],
            fecha_emision=self.row['fecha_emision'],
            inicio_vigencia=self.row['inicio_vigencia'],
            fin_vigencia=self.row['fin_vigencia']
        )