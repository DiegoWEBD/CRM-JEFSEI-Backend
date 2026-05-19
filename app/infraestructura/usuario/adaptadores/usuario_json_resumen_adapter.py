from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.usuario.dto.usuario_json_resumen import UsuarioJsonResumen


class UsuarioJsonResumenAdapter:
    def __init__(self, usuario: Usuario):
        self.usuario = usuario

    def to_usuario_json_resumen(self) -> UsuarioJsonResumen:
        return UsuarioJsonResumen(
            rut=self.usuario.rut,
            nombre=self.usuario.nombre
        )