from psycopg.rows import DictRow

from app.dominio.administrador_condominio.administrador_condominio import (
    AdministradorCondominio,
)


class DictRowAdministradorAdapter:

    def __init__(self, row: DictRow):
        if row is None:
            raise ValueError("Administrador inválido")

        self.row = row

    def to_administrador(self) -> AdministradorCondominio:
        return AdministradorCondominio(
            id=self.row["id"],
            nombre_administrador=self.row["nombre_administrador"],
            nombre_contacto=self.row["nombre_contacto"],
            telefono=self.row["telefono"],
            correo=self.row["correo"],
        )
