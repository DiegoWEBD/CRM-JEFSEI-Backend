from psycopg.rows import TupleRow

from app.dominio.linea_negocio.linea_negocio import LineaNegocio


class TupleRowLineaNegocioAdapter:

    def __init__(self, row: TupleRow):

        if not row:
            raise Exception('Línea de negocio inválida')

        self.row = row

    def to_linea_negocio(self) -> LineaNegocio:
         id = self.row['id_linea_negocio']
         nombre = self.row['nombre_linea_negocio']

         return LineaNegocio(
             id=id,
             nombre=nombre
         )