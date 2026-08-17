from psycopg.rows import DictRow

from app.dominio.contacto.contacto import Contacto


class DictRowContactoAdapter:

    def __init__(self, row: DictRow):
        if row is None:
            raise ValueError("Contacto inválido")

        self.row = row

    def to_contacto(self) -> Contacto:
        return Contacto(
            id=self.row["id"],
            id_prospecto=self.row["id_prospecto"],
            nombre=self.row["nombre"],
            telefono=self.row["telefono"],
            correo=self.row["correo"],
            cargo=self.row["cargo"],
        )