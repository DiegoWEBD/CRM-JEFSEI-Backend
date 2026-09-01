from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.producto.repositorio_producto import RepositorioProducto
from app.dominio.producto.producto import Producto


class CrearProductoUseCase:
    def __init__(self, repositorio_producto: RepositorioProducto):
        self.repositorio_producto = repositorio_producto

    def ejecutar(
        self,
        nombre: str,
        id_linea_negocio: int,
        codigo: str | None = None,
    ) -> bool:
        if not nombre or not nombre.strip():
            raise ConflictoEnAccionException("El nombre del producto es obligatorio")

        if not id_linea_negocio or id_linea_negocio <= 0:
            raise ConflictoEnAccionException("La línea de negocio es obligatoria")

        producto = Producto(
            nombre=nombre.strip(),
            id_linea_negocio=id_linea_negocio,
            codigo=codigo,
            eliminado=False,
        )

        return self.repositorio_producto.crear(producto)
