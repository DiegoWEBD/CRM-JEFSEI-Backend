class UsuarioNoAutorizadoException(Exception):
    def __init__(self, mensaje: str = 'Usuario no autorizado'):
        super().__init__(mensaje)