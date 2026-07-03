from psycopg.rows import DictRow

from app.dominio.sucursal.sucursal import Sucursal


class DictRowSucursalAdapter:

    def __init__(self, row: DictRow) -> None:
        self.row = row

    def to_sucursal(self) -> Sucursal:
        return Sucursal(
            id=self.row['id'],
            nombre=self.row['nombre']
        )