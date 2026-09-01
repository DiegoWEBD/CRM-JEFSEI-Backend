import pytest
from unittest.mock import MagicMock

from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.linea_negocio.deps import get_obtener_productos_linea_negocio_use_case
from app.aplicacion.linea_negocio.use_cases.obtener_productos_linea_negocio import ObtenerProductosLineaNegocioUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from tests.factories.usuario_factory import crear_usuario_admin_mock
from tests.factories.producto_factory import crear_producto_mock
from tests.factories.linea_negocio_factory import crear_linea_negocio_mock
from tests.factories.auth_factory import crear_token_mock, headers_auth


@pytest.fixture
def usuario_autenticado():
    return crear_usuario_admin_mock()


@pytest.fixture
def headers_auth_validos(token_valido):
    return headers_auth(token_valido)


@pytest.fixture
def token_valido():
    return crear_token_mock()


@pytest.fixture
def client(usuario_autenticado):
    def override_get_current_user():
        return usuario_autenticado

    app.dependency_overrides[get_current_user] = override_get_current_user

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_con_productos(usuario_autenticado):
    def override_get_current_user():
        return usuario_autenticado

    def override_get_obtener_productos():
        uc = MagicMock(spec=ObtenerProductosLineaNegocioUseCase)
        uc.ejecutar.return_value = [
            crear_producto_mock(id=1, nombre="Seguro de Vida"),
            crear_producto_mock(id=2, nombre="Seguro de Auto"),
        ]
        return uc

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_productos_linea_negocio_use_case] = override_get_obtener_productos

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_linea_no_encontrada(usuario_autenticado):
    def override_get_current_user():
        return usuario_autenticado

    def override_get_obtener_productos():
        uc = MagicMock(spec=ObtenerProductosLineaNegocioUseCase)
        uc.ejecutar.side_effect = RecursoNoEncontradoException('Línea de negocio no encontrada')
        return uc

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_productos_linea_negocio_use_case] = override_get_obtener_productos

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestLineaNegocioProductosEndpoints:

    def test_obtener_productos_linea_negocio_exitoso(self, client_con_productos, headers_auth_validos):
        response = client_con_productos.get("/lineas-negocio/1/productos", headers=headers_auth_validos)

        assert response.status_code == 200
        data = response.json()
        assert "productos" in data
        assert len(data["productos"]) == 2
        assert data["productos"][0]["nombre"] == "Seguro de Vida"
        assert data["productos"][1]["nombre"] == "Seguro de Auto"

    def test_obtener_productos_linea_negocio_no_encontrada(self, client_linea_no_encontrada, headers_auth_validos):
        response = client_linea_no_encontrada.get("/lineas-negocio/999/productos", headers=headers_auth_validos)

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Línea de negocio no encontrada"

    def test_obtener_productos_sin_autenticacion(self):
        from app.main import app as real_app
        from starlette.testclient import TestClient

        real_app.dependency_overrides.clear()
        with TestClient(real_app) as c:
            response = c.get("/lineas-negocio/1/productos")

        assert response.status_code == 401
