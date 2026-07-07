from psycopg.rows import DictRow

from app.dominio.rol.rol import Rol


class DictRowRolAdapter:

    def __init__(self, row: DictRow):
        self.row = row

    def to_rol(self) -> Rol:
        return Rol(
            codigo=self.row['codigo'],
            nombre=self.row['nombre']
        )
