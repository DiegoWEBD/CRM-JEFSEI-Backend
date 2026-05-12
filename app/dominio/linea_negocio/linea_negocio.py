from app.dominio.producto.producto import Producto


class LineaNegocio:
    def __init__(
        self, 
        nombre: str,
        productos: list[Producto] = [],
        id: int | None = None
    ):
        self.id = id
        self.nombre = nombre
        self.productos = productos