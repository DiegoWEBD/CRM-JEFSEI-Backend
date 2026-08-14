from app.dominio.contacto.contacto import Contacto
from app.presentacion.api.contacto.dto.contacto_json import ContactoJson


class ContactoJsonAdapter:

    def __init__(self, contacto: Contacto):
        self.contacto = contacto

    def to_json(self) -> ContactoJson:
        if self.contacto.id is None:
            raise Exception('Contacto inválido')

        return ContactoJson(
            id=self.contacto.id,
            id_prospecto=self.contacto.id_prospecto,
            nombre=self.contacto.nombre,
            telefono=self.contacto.telefono,
            correo=self.contacto.correo,
            cargo=self.contacto.cargo,
        )