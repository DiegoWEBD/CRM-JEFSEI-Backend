from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio
from app.dominio.producto.repositorio_producto import RepositorioProducto
from app.dominio.producto.producto import Producto
from app.infraestructura.lib.normalizar_texto import normalizar_texto


class CrearProductoUseCase:
    def __init__(
        self,
        repositorio_producto: RepositorioProducto,
        repositorio_linea_negocio: RepositorioLineasNegocio,
    ):
        self.repositorio_producto = repositorio_producto
        self.repositorio_linea_negocio = repositorio_linea_negocio

    def ejecutar(
        self,
        nombre: str,
        id_linea_negocio: int,
    ) -> bool:
        if not nombre or not nombre.strip():
            raise ConflictoEnAccionException("El nombre del producto es obligatorio")

        if not id_linea_negocio or id_linea_negocio <= 0:
            raise ConflictoEnAccionException("La línea de negocio es obligatoria")

        if self.repositorio_producto.existe_por_nombre_y_linea_negocio(
            nombre, id_linea_negocio
        ):
            raise RecursoYaExisteException(
                "Ya existe un producto con ese nombre para la línea de negocio seleccionada"
            )

        linea_negocio = self.repositorio_linea_negocio.obtener_por_id(id_linea_negocio)
        if not linea_negocio:
            raise ConflictoEnAccionException("La línea de negocio no existe")

        codigo = f"{normalizar_texto(nombre)}_{normalizar_texto(linea_negocio.nombre)}"

        producto = Producto(
            nombre=nombre.strip(),
            id_linea_negocio=id_linea_negocio,
            codigo=codigo,
            eliminado=False,
        )

        return self.repositorio_producto.crear(producto)
