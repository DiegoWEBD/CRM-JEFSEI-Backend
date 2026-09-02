from app.dominio.producto.producto import Producto


def crear_producto_mock(
    id: int = 1,
    nombre: str = "Seguro de Vida",
    id_linea_negocio: int = 10,
    codigo: str | None = "VIDA-001",
    eliminado: bool = False,
) -> Producto:
    return Producto(
        id=id,
        nombre=nombre,
        id_linea_negocio=id_linea_negocio,
        codigo=codigo,
        eliminado=eliminado,
    )
