from app.dominio.linea_negocio.linea_negocio import LineaNegocio
from app.dominio.producto.producto import Producto


def crear_linea_negocio_mock(
    id: int = 1,
    nombre: str = "Línea de Negocio Test",
    productos: list[Producto] | None = None,
) -> LineaNegocio:
    if productos is None:
        productos = []
    return LineaNegocio(id=id, nombre=nombre, productos=productos)
