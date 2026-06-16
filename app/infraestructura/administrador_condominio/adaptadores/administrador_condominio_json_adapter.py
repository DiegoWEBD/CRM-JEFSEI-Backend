from app.dominio.administrador_condominio.administrador_condominio import AdministradorCondominio
from app.presentacion.api.administrador_condominio.dto.administrador_condominio_json import AdministradorCondominioJson


class AdministradorCondominioJsonAdapter:

    def __init__(self, administrador: AdministradorCondominio):
        self.administrador = administrador

    def to_json(self) -> AdministradorCondominioJson:
        if self.administrador.id is None:
            raise Exception('Administrador inválido')
        
        return AdministradorCondominioJson(
            id=self.administrador.id,
            nombre_administrador=self.administrador.nombre_administrador,
            nombre_contacto=self.administrador.nombre_contacto,
            telefono=self.administrador.telefono,
            correo=self.administrador.correo
        )