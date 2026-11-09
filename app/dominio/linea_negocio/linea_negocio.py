from app.dominio.producto.producto import Producto

# Códigos de las líneas de negocio soportadas (LineaNegocio.codigo).
CODIGO_LINEA_CONDOMINIOS = 'condominios'
CODIGO_LINEAS_PERSONALES = 'lineas_personales'
CODIGO_LINEAS_COMERCIALES = 'lineas_comerciales'


class LineaNegocio:
    def __init__(
        self, 
        nombre: str,
        codigo: str,
        productos: list[Producto] = [],
        id: int | None = None,
    ):
        self.id = id
        self.nombre = nombre
        self.productos = productos
        self.codigo = codigo
