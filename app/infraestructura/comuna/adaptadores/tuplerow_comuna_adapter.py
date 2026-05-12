from psycopg.rows import TupleRow

from app.dominio.comuna.comuna import Comuna


class TupleRowComunaAdapter:

    def __init__(self, row: TupleRow): 
        if row is None:
            raise ValueError('Comuna inválida')
        
        self.row = row

    def to_comuna(self) -> Comuna:
        return Comuna(
            id=self.row['id'],
            nombre=self.row['nombre']
        )