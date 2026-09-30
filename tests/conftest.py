import os

# El job programado de alertas no debe correr durante los tests
os.environ.setdefault('CRM_INICIAR_SCHEDULER', 'false')

import pytest
from unittest.mock import MagicMock

from app.aplicacion.auditoria.audit_service import AuditService
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.aplicacion.auth.authentication_service import AuthenticationService
from app.main import app
from app.presentacion.api.auth.dependencias.get_sesion_use_cases import get_audit_service
from tests.factories.usuario_factory import crear_usuario_mock, crear_usuario_admin_mock
from tests.factories.auth_factory import crear_token_mock, headers_auth


@pytest.fixture(autouse=True)
def auditoria_aislada():
    """Desconecta la auditoría en los tests por defecto.

    Los eventos críticos escriben fail-closed: sin la tabla ``AuditoriaEvento``
    levantada, cualquier 403 real se convertiría en 500 y los tests de
    autorización y de negocio no podrían medir lo que miden. Los tests que sí
    verifican auditoría quitan este override explícitamente.
    """
    original = app.dependency_overrides.get(get_audit_service)

    def _fake():
        servicio = MagicMock(spec=AuditService)
        # con_usuario devuelve el scope para que el código que encadena
        # contexto -> log siga funcionando sin efectos.
        servicio.con_usuario.side_effect = (
            lambda scope, rut_usuario, id_sesion=None: scope
        )
        return servicio

    app.dependency_overrides[get_audit_service] = _fake
    yield
    if original is None:
        app.dependency_overrides.pop(get_audit_service, None)
    else:
        app.dependency_overrides[get_audit_service] = original


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
