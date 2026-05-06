class Comuna:
    
    def __init__(
        self,
        nombre: str,
        id: int | None = None
    ):
        self.id = id
        self.nombre = nombre