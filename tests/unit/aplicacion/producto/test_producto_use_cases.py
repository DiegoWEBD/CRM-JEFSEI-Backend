import pytest
from unittest.mock import MagicMock, call

from app.dominio.producto.producto import Producto
from app.dominio.producto.repositorio_producto import RepositorioProducto
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from tests.factories.producto_factory import crear_producto_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioProducto)


@pytest.mark.unit
class TestObtenerProductosUseCase:

    def test_obtener_productos_lista(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.obtener_productos import ObtenerProductosUseCase

        productos = [
            crear_producto_mock(id=1, nombre="Seguro de Vida"),
            crear_producto_mock(id=2, nombre="Seguro Automotriz"),
        ]
        repositorio_mock.obtener_activos.return_value = (productos, 2)

        uc = ObtenerProductosUseCase(repositorio_mock)
        productos_resultado, total = uc.ejecutar()

        assert len(productos_resultado) == 2
        assert total == 2
        repositorio_mock.obtener_activos.assert_called_once_with(
            id_linea_negocio=None,
            texto_busqueda=None,
            pagina=1,
            tamano_pagina=20,
        )

    def test_obtener_productos_lista_vacia(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.obtener_productos import ObtenerProductosUseCase

        repositorio_mock.obtener_activos.return_value = ([], 0)

        uc = ObtenerProductosUseCase(repositorio_mock)
        productos_resultado, total = uc.ejecutar()

        assert len(productos_resultado) == 0
        assert total == 0

    def test_obtener_productos_con_filtro_linea_negocio(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.obtener_productos import ObtenerProductosUseCase

        productos = [crear_producto_mock(id=1, id_linea_negocio=10)]
        repositorio_mock.obtener_activos.return_value = (productos, 1)

        uc = ObtenerProductosUseCase(repositorio_mock)
        productos_resultado, total = uc.ejecutar(id_linea_negocio=10)

        assert len(productos_resultado) == 1
        assert total == 1
        repositorio_mock.obtener_activos.assert_called_once_with(
            id_linea_negocio=10,
            texto_busqueda=None,
            pagina=1,
            tamano_pagina=20,
        )

    def test_obtener_productos_con_texto_busqueda(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.obtener_productos import ObtenerProductosUseCase

        productos = [crear_producto_mock(id=1, nombre="Seguro de Vida")]
        repositorio_mock.obtener_activos.return_value = (productos, 1)

        uc = ObtenerProductosUseCase(repositorio_mock)
        productos_resultado, total = uc.ejecutar(texto_busqueda="vida")

        assert len(productos_resultado) == 1
        assert total == 1
        repositorio_mock.obtener_activos.assert_called_once_with(
            id_linea_negocio=None,
            texto_busqueda="vida",
            pagina=1,
            tamano_pagina=20,
        )

    def test_obtener_productos_con_paginacion(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.obtener_productos import ObtenerProductosUseCase

        productos = [crear_producto_mock(id=3, nombre="Seguro Hogar")]
        repositorio_mock.obtener_activos.return_value = (productos, 25)

        uc = ObtenerProductosUseCase(repositorio_mock)
        productos_resultado, total = uc.ejecutar(pagina=2, tamano_pagina=10)

        assert len(productos_resultado) == 1
        assert total == 25
        repositorio_mock.obtener_activos.assert_called_once_with(
            id_linea_negocio=None,
            texto_busqueda=None,
            pagina=2,
            tamano_pagina=10,
        )

    def test_obtener_productos_filtros_combinados(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.obtener_productos import ObtenerProductosUseCase

        productos = [crear_producto_mock(id=1, nombre="Seguro Vida", id_linea_negocio=10)]
        repositorio_mock.obtener_activos.return_value = (productos, 1)

        uc = ObtenerProductosUseCase(repositorio_mock)
        productos_resultado, total = uc.ejecutar(
            id_linea_negocio=10,
            texto_busqueda="vida",
            pagina=1,
            tamano_pagina=5,
        )

        assert len(productos_resultado) == 1
        assert total == 1
        repositorio_mock.obtener_activos.assert_called_once_with(
            id_linea_negocio=10,
            texto_busqueda="vida",
            pagina=1,
            tamano_pagina=5,
        )


@pytest.mark.unit
class TestObtenerProductoUseCase:

    def test_obtener_producto_exitoso(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.obtener_producto import ObtenerProductoUseCase

        producto = crear_producto_mock(id=1)
        repositorio_mock.obtener_por_id.return_value = producto

        uc = ObtenerProductoUseCase(repositorio_mock)
        resultado = uc.ejecutar(1)

        assert resultado.id == 1
        assert resultado.nombre == "Seguro de Vida"

    def test_obtener_producto_no_encontrado(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.obtener_producto import ObtenerProductoUseCase

        repositorio_mock.obtener_por_id.return_value = None

        uc = ObtenerProductoUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Producto no encontrado"):
            uc.ejecutar(999)

    def test_obtener_producto_eliminado(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.obtener_producto import ObtenerProductoUseCase

        repositorio_mock.obtener_por_id.return_value = None

        uc = ObtenerProductoUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Producto no encontrado"):
            uc.ejecutar(1)


@pytest.mark.unit
class TestCrearProductoUseCase:

    def test_crear_producto_exitoso(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.crear_producto import CrearProductoUseCase

        repositorio_mock.obtener_por_id.return_value = None
        repositorio_mock.crear.return_value = True

        uc = CrearProductoUseCase(repositorio_mock)
        resultado = uc.ejecutar(
            nombre="Seguro Hogar",
            id_linea_negocio=10,
            codigo="HOGAR-001",
        )

        assert resultado is True
        repositorio_mock.crear.assert_called_once()
        producto_creado = repositorio_mock.crear.call_args[0][0]
        assert producto_creado.nombre == "Seguro Hogar"
        assert producto_creado.id_linea_negocio == 10
        assert producto_creado.codigo == "HOGAR-001"
        assert producto_creado.eliminado is False

    def test_crear_producto_nombre_vacio(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.crear_producto import CrearProductoUseCase

        uc = CrearProductoUseCase(repositorio_mock)

        with pytest.raises(ConflictoEnAccionException, match="El nombre del producto es obligatorio"):
            uc.ejecutar(
                nombre="",
                id_linea_negocio=10,
                codigo="HOGAR-001",
            )

    def test_crear_producto_sin_linea_negocio(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.crear_producto import CrearProductoUseCase

        uc = CrearProductoUseCase(repositorio_mock)

        with pytest.raises(ConflictoEnAccionException, match="La línea de negocio es obligatoria"):
            uc.ejecutar(
                nombre="Seguro Hogar",
                id_linea_negocio=0,
                codigo="HOGAR-001",
            )


@pytest.mark.unit
class TestActualizarProductoUseCase:

    def test_actualizar_producto_exitoso(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.actualizar_producto import ActualizarProductoUseCase

        producto_existente = crear_producto_mock(id=1)
        repositorio_mock.obtener_por_id.return_value = producto_existente
        repositorio_mock.actualizar.return_value = True

        uc = ActualizarProductoUseCase(repositorio_mock)
        resultado = uc.ejecutar(
            id=1,
            nombre="Seguro Hogar Actualizado",
            id_linea_negocio=11,
            codigo="HOGAR-002",
        )

        assert resultado is True
        repositorio_mock.actualizar.assert_called_once()
        producto_actualizado = repositorio_mock.actualizar.call_args[0][0]
        assert producto_actualizado.nombre == "Seguro Hogar Actualizado"
        assert producto_actualizado.id_linea_negocio == 11

    def test_actualizar_producto_no_encontrado(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.actualizar_producto import ActualizarProductoUseCase

        repositorio_mock.obtener_por_id.return_value = None

        uc = ActualizarProductoUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Producto no encontrado"):
            uc.ejecutar(
                id=999,
                nombre="Test",
                id_linea_negocio=10,
                codigo="TEST",
            )

    def test_actualizar_producto_eliminado(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.actualizar_producto import ActualizarProductoUseCase

        repositorio_mock.obtener_por_id.return_value = None

        uc = ActualizarProductoUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Producto no encontrado"):
            uc.ejecutar(
                id=1,
                nombre="Test",
                id_linea_negocio=10,
                codigo="TEST",
            )

    def test_actualizar_producto_nombre_vacio(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.actualizar_producto import ActualizarProductoUseCase

        producto = crear_producto_mock(id=1)
        repositorio_mock.obtener_por_id.return_value = producto

        uc = ActualizarProductoUseCase(repositorio_mock)

        with pytest.raises(ConflictoEnAccionException, match="El nombre del producto es obligatorio"):
            uc.ejecutar(
                id=1,
                nombre="",
                id_linea_negocio=10,
                codigo="TEST",
            )


@pytest.mark.unit
class TestEliminarProductoUseCase:

    def test_eliminar_producto_exitoso(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.eliminar_producto import EliminarProductoUseCase

        producto = crear_producto_mock(id=1, eliminado=False)
        repositorio_mock.obtener_por_id.return_value = producto
        repositorio_mock.eliminar.return_value = True

        uc = EliminarProductoUseCase(repositorio_mock)
        uc.ejecutar(1)

        repositorio_mock.eliminar.assert_called_once_with(1)

    def test_eliminar_producto_no_encontrado(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.eliminar_producto import EliminarProductoUseCase

        repositorio_mock.obtener_por_id.return_value = None

        uc = EliminarProductoUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Producto no encontrado"):
            uc.ejecutar(999)

    def test_eliminar_producto_ya_eliminado(self, repositorio_mock):
        from app.aplicacion.producto.use_cases.eliminar_producto import EliminarProductoUseCase

        producto = crear_producto_mock(id=1, eliminado=True)
        repositorio_mock.obtener_por_id.return_value = None

        uc = EliminarProductoUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Producto no encontrado"):
            uc.ejecutar(1)
