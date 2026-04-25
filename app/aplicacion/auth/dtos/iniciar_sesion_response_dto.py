from app.dominio.usuario.usuario import Usuario


class IniciarSesionResponseDTO:
    def __init__(
        self,
        access_token: str,
        usuario: Usuario
    ):
        self.access_token = access_token
        self.token_type = 'bearer'
        self.usuario = usuario