from datetime import datetime

from app.dominio.gestion_comercial.gestion_comercial import GestionComercial
from app.presentacion.api.gestion_comercial.dto.gestion_comercial_json import GestionComercialJson


class GestionComercialJsonAdapter:

    def __init__(self, gestion: GestionComercial) -> None:
        self.gestion = gestion

    def to_json(self) -> GestionComercialJson:
        return GestionComercialJson(
            id=self.gestion.id,
            tipo=self.gestion.tipo,
            rut_usuario=self.gestion.rut_usuario,
            nombre_ejecutivo=self.gestion.nombre_ejecutivo,
            id_prospecto=self.gestion.id_prospecto,
            nombre_cliente=self.gestion.nombre_cliente,
            titulo=self.gestion.titulo,
            estado_contacto=self.gestion.estado_contacto,
            observacion=self.gestion.observacion,
            created_at=self.gestion.created_at,
            fecha_gestion=self.gestion.fecha_gestion,
        )
