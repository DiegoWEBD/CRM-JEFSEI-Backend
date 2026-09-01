class Producto:
    def __init__(
        self,
        nombre: str,
        id_linea_negocio: int,
        codigo: str | None = None,
        eliminado: bool = False,
        id: int | None = None
    ):
        self.id = id
        self.nombre = nombre
        self.id_linea_negocio = id_linea_negocio
        self.codigo = codigo
        self.eliminado = eliminado