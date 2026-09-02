import pytest
from unittest.mock import MagicMock

from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.aplicacion.auth.authentication_service import AuthenticationService
from tests.factories.usuario_factory import crear_usuario_mock, crear_usuario_admin_mock
from tests.factories.auth_factory import crear_token_mock, headers_auth


@pytest.fixture
def mock_repositorio_usuarios():
    repo = MagicMock(spec=RepositorioUsuarios)
    return repo


@pytest.fixture
def mock_auth_service():
    service = MagicMock(spec=AuthenticationService)
    service.hash_password.return_value = "hashed_password_123"
    service.verificar_password.return_value = True
    service.crear_access_token.return_value = "mock_jwt_token"
    return service


@pytest.fixture
def usuario_mock():
    return crear_usuario_mock()


@pytest.fixture
def usuario_admin_mock():
    return crear_usuario_admin_mock()


@pytest.fixture
def token_valido():
    return crear_token_mock()


@pytest.fixture
def headers_auth_validos(token_valido):
    return headers_auth(token_valido)
