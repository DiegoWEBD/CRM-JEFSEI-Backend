from psycopg.rows import DictRow

from app.dominio.permiso.permiso import Permiso


class DictRowPermisoAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_permiso(self) -> Permiso:
        return Permiso(
            codigo=self.row['codigo'],
            descripcion=self.row['descripcion']
        )
