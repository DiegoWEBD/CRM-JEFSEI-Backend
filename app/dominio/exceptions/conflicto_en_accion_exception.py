class ConflictoEnAccionException(Exception):
    def __init__(self, mensaje: str = 'No se puede procesar la acción'):
        super().__init__(mensaje)