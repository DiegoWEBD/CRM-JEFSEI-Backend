from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.producto.repositorio_producto import RepositorioProducto
from app.dominio.producto.producto import Producto


class ActualizarProductoUseCase:
    def __init__(self, repositorio_producto: RepositorioProducto):
        self.repositorio_producto = repositorio_producto

    def ejecutar(
        self,
        id: int,
        nombre: str,
        id_linea_negocio: int,
    ) -> bool:
        producto = self.repositorio_producto.obtener_por_id(id)

        if producto is None:
            raise RecursoNoEncontradoException("Producto no encontrado")

        if not nombre or not nombre.strip():
            raise ConflictoEnAccionException("El nombre del producto es obligatorio")

        producto.nombre = nombre.strip()
        producto.id_linea_negocio = id_linea_negocio

        return self.repositorio_producto.actualizar(producto)
