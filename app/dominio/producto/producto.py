class Producto:
    def __init__(
        self,
        nombre: str,
        codigo: str,
        id: int | None = None
    ):
        self.id = id
        self.nombre = nombre
        self.codigo = codigo