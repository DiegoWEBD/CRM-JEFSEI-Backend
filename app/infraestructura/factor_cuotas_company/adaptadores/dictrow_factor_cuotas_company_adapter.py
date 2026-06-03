from psycopg.rows import DictRow

from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany


class DictRowFactorCuotasCompanyAdapter:

    def __init__(self, row: DictRow) -> None:
        self.row = row

    def to_factor_cuotas_company(self) -> FactorCuotasCompany:
        
        numero_cuotas = self.row['numero_cuotas']
        factor = self.row['factor']

        return FactorCuotasCompany(
            numero_cuotas=numero_cuotas,
            factor=factor
        )