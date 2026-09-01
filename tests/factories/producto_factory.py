from app.dominio.producto.producto import Producto


def crear_producto_mock(
    id: int = 1,
    nombre: str = "Producto Test",
    codigo: str = "PROD-001",
) -> Producto:
    return Producto(id=id, nombre=nombre, codigo=codigo)
