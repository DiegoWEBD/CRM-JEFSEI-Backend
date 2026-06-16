from psycopg.rows import DictRow

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.cotizacion.cotizacion import Cotizacion


class DictRowCotizacionAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_cotizacion(self) -> Cotizacion:
        company = CompanySeguros(
            id=self.row['id_company'],
            nombre=self.row['nombre_company']
        )

        return Cotizacion(
            id=self.row['id'],
            monto_total_asegurado=self.row['monto_total_asegurado'],
            tasa_afecta=self.row['tasa_afecta'],
            tasa_excenta=self.row['tasa_excenta'],
            tasa_politica=self.row['tasa_politica'],
            prima_adicional_asistencia=self.row['prima_adicional_asistencia'],
            fecha_emision=self.row['fecha_emision'],
            fecha_vencimiento=self.row['fecha_vencimiento'],
            company=company
        )