from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio
from app.dominio.producto.producto import Producto


class ObtenerProductosLineaNegocioUseCase:

    def __init__(self, repositorio_lineas_negocio: RepositorioLineasNegocio):
        self.repositorio_lineas_negocio = repositorio_lineas_negocio

    def ejecutar(self, id_linea_negocio: int) -> list[Producto]:
        linea_negocio = self.repositorio_lineas_negocio.obtener_por_id(id_linea_negocio)

        if linea_negocio is None:
            raise RecursoNoEncontradoException('Línea de negocio no encontrada')

        return self.repositorio_lineas_negocio.obtener_productos_por_linea_negocio(id_linea_negocio)
