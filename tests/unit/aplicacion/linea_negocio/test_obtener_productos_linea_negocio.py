import pytest
from unittest.mock import MagicMock

from app.aplicacion.linea_negocio.use_cases.obtener_productos_linea_negocio import ObtenerProductosLineaNegocioUseCase
from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from tests.factories.producto_factory import crear_producto_mock
from tests.factories.linea_negocio_factory import crear_linea_negocio_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioLineasNegocio)


@pytest.mark.unit
class TestObtenerProductosLineaNegocioUseCase:

    def test_obtener_productos_exitoso(self, repositorio_mock):
        linea_negocio = crear_linea_negocio_mock(id=1)
        productos = [
            crear_producto_mock(id=1, nombre="Seguro de Vida"),
            crear_producto_mock(id=2, nombre="Seguro de Auto"),
        ]
        repositorio_mock.obtener_por_id.return_value = linea_negocio
        repositorio_mock.obtener_productos_por_linea_negocio.return_value = productos

        uc = ObtenerProductosLineaNegocioUseCase(repositorio_mock)
        resultado = uc.ejecutar(1)

        assert len(resultado) == 2
        assert resultado[0].nombre == "Seguro de Vida"
        assert resultado[1].nombre == "Seguro de Auto"
        repositorio_mock.obtener_por_id.assert_called_once_with(1)
        repositorio_mock.obtener_productos_por_linea_negocio.assert_called_once_with(1)

    def test_obtener_productos_linea_negocio_no_encontrada(self, repositorio_mock):
        repositorio_mock.obtener_por_id.return_value = None

        uc = ObtenerProductosLineaNegocioUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException, match="Línea de negocio no encontrada"):
            uc.ejecutar(999)

        repositorio_mock.obtener_por_id.assert_called_once_with(999)
        repositorio_mock.obtener_productos_por_linea_negocio.assert_not_called()

    def test_obtener_productos_lista_vacia(self, repositorio_mock):
        linea_negocio = crear_linea_negocio_mock(id=1)
        repositorio_mock.obtener_por_id.return_value = linea_negocio
        repositorio_mock.obtener_productos_por_linea_negocio.return_value = []

        uc = ObtenerProductosLineaNegocioUseCase(repositorio_mock)
        resultado = uc.ejecutar(1)

        assert len(resultado) == 0
        repositorio_mock.obtener_por_id.assert_called_once_with(1)
        repositorio_mock.obtener_productos_por_linea_negocio.assert_called_once_with(1)
