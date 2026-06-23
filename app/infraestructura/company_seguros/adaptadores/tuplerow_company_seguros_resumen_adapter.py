from psycopg.rows import DictRow

from app.dominio.company_seguros.company_seguros import CompanySeguros


class TupleRowCompanySegurosResumenAdapter:

    def __init__(self, row: DictRow):
        if row is None:
            raise ValueError('Compañía inválida')

        self.row = row

    def to_company_seguros(self) -> CompanySeguros:
        return CompanySeguros(
            id=self.row['id'],
            nombre=self.row['nombre'],
        )
