from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.usuario.schemas.usuario_json import UsuarioJson


class UsuarioJsonAdapter(UsuarioJson):
    def __init__(self, usuario: Usuario):
        super().__init__(
            rut=usuario.rut,
            nombre=usuario.nombre,
            correo=usuario.correo,
            telefono=usuario.telefono,
            sucursal=usuario.sucursal,
            roles=usuario.roles
        )