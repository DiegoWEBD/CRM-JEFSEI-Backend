class BadRequestException(Exception):
    def __init__(self, mensaje: str = 'Solicitud inválida'):
        super().__init__(mensaje)