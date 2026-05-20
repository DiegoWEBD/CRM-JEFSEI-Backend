from psycopg.rows import TupleRow

from app.dominio.company_seguros.company_seguros import CompanySeguros
from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany


class TupleRowsCompanySegurosAdapter:

    def __init__(self, rows: list[TupleRow]):
        if not rows or len(rows) == 0:
            raise Exception('Compañia inválida')
        
        self.rows = rows

    def to_company_seguros(self) -> CompanySeguros:
        
        id = self.rows[0]['id']
        nombre = self.rows[0]['nombre']
        nombre_logo = self.rows[0]['nombre_logo']

        factores: list[FactorCuotasCompany] = []

        for row in self.rows:
            numero_cuotas = row['numero_cuotas']
            factor = row['factor']

            factor_cuotas = FactorCuotasCompany(
                numero_cuotas=numero_cuotas,
                factor=factor
            )

            factores.append(factor_cuotas)

        return CompanySeguros(
            id=id,
            nombre=nombre,
            nombre_logo=nombre_logo,
            factores_cuotas=factores,
            coberturas=[]
        )