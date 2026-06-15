class RecursoNoEncontradoException(Exception):
    def __init__(self, mensaje: str = 'Recurso no encontrado'):
        super().__init__(mensaje)