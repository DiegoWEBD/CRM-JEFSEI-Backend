from app.dominio.producto.repositorio_producto import RepositorioProducto
from app.dominio.producto.producto import Producto


class ObtenerProductosUseCase:
    def __init__(self, repositorio_producto: RepositorioProducto):
        self.repositorio_producto = repositorio_producto

    def ejecutar(
        self,
        id_linea_negocio: int | None = None,
        texto_busqueda: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 20,
    ) -> tuple[list[Producto], int]:
        return self.repositorio_producto.obtener_activos(
            id_linea_negocio=id_linea_negocio,
            texto_busqueda=texto_busqueda,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )
