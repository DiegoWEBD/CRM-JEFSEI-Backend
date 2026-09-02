from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.producto.repositorio_producto import RepositorioProducto
from app.dominio.producto.producto import Producto


class ObtenerProductoUseCase:
    def __init__(self, repositorio_producto: RepositorioProducto):
        self.repositorio_producto = repositorio_producto

    def ejecutar(self, id: int) -> Producto:
        producto = self.repositorio_producto.obtener_por_id(id)

        if producto is None:
            raise RecursoNoEncontradoException("Producto no encontrado")

        return producto
