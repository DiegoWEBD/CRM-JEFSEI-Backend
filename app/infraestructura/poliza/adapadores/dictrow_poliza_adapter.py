from datetime import datetime

from psycopg.rows import DictRow

from app.dominio.poliza.estado_poliza.estado_poliza import EstadoPoliza
from app.dominio.poliza.poliza import Poliza


class DictRowPolizaAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_poliza(self) -> Poliza:

        cancelada: bool | None = self.row['cancelada']
        fin_vigencia: datetime | None = self.row['fin_vigencia']
        estado: EstadoPoliza = EstadoPoliza.REGISTRADA

        if cancelada:
            estado = EstadoPoliza.CANCELADA
        elif fin_vigencia is not None:
            datetime_actual = datetime.now()

            if fin_vigencia < datetime_actual:
                estado = EstadoPoliza.VENCIDA

            diferencia_dias = (fin_vigencia - datetime_actual).days

            if diferencia_dias <= 10:
                estado = EstadoPoliza.POR_VENCER
            else:
                estado = EstadoPoliza.VIGENTE


        return Poliza(
            numero_poliza=self.row['numero_poliza'],
            tipo=self.row['tipo'],
            nombre_producto=self.row['nombre_producto'],
            company=self.row['company'],
            prima_neta=self.row['prima_neta'],
            comision_corredora_pct=self.row['comision_corredora_pct'],
            fecha_emision=self.row['fecha_emision'],
            inicio_vigencia=self.row['inicio_vigencia'],
            fin_vigencia=fin_vigencia,
            estado=estado
        )