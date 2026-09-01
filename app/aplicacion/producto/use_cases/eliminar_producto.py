from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.producto.repositorio_producto import RepositorioProducto


class EliminarProductoUseCase:
    def __init__(self, repositorio_producto: RepositorioProducto):
        self.repositorio_producto = repositorio_producto

    def ejecutar(self, id: int) -> None:
        producto = self.repositorio_producto.obtener_por_id(id)

        if producto is None:
            raise RecursoNoEncontradoException("Producto no encontrado")

        self.repositorio_producto.eliminar(id)
