class RecursoYaExisteException(Exception):
    def __init__(self, mensaje: str = 'El recurso que intenta crear ya existe'):
        super().__init__(mensaje)