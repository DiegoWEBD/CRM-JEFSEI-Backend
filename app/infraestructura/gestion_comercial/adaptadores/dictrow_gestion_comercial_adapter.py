from datetime import datetime

from app.dominio.gestion_comercial.gestion_comercial import GestionComercial


class DictRowGestionComercialAdapter:

    def __init__(self, row: dict) -> None:
        self.row = row

    def to_gestion_comercial(self) -> GestionComercial:
        return GestionComercial(
            id=self.row['id'],
            tipo=self.row['tipo'],
            rut_usuario=self.row['rut_usuario'],
            nombre_ejecutivo=self.row.get('nombre_ejecutivo'),
            id_prospecto=self.row['id_prospecto'],
            nombre_cliente=self.row.get('nombre_cliente'),
            titulo=self.row['titulo'],
            estado_contacto=self.row.get('estado_contacto'),
            observacion=self.row.get('observacion'),
            created_at=self.row['created_at'],
            fecha_gestion=self.row['fecha_gestion'],
        )
