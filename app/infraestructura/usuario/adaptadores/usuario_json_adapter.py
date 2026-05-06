from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.usuario.dto.usuario_json import UsuarioJson


class UsuarioJsonAdapter:

    @staticmethod
    def Adapt(usuario: Usuario) -> UsuarioJson:
        return UsuarioJson(
            rut=usuario.rut,
            nombre=usuario.nombre,
            correo=usuario.correo,
            telefono=usuario.telefono,
            sucursal=usuario.sucursal.nombre,
            meta_mensual_uf=usuario.meta_mensual_uf,
            roles=[rol.nombre for rol in usuario.roles]
        )