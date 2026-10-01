import pytest
from unittest.mock import MagicMock

from app.main import app
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from app.aplicacion.auth.authentication_service import AuthenticationService
from app.aplicacion.auditoria.audit_service import AuditService
from app.dominio.auditoria.repositorio_sesiones import RepositorioSesiones
from app.infraestructura.auditoria.repositorio_sesiones_postgres import RepositorioSesionesPostgres
from app.presentacion.api.auth.dependencias.get_current_user import (
    get_current_user,
    get_repositorio_sesiones_dep,
)
from app.presentacion.api.auth.dependencias.get_iniciar_sesion_use_case import get_iniciar_sesion_use_case
from app.presentacion.api.auth.dependencias.get_sesion_use_cases import get_audit_service
from app.presentacion.api.usuario.deps import (
    get_obtener_usuario_use_case,
    get_obtener_usuarios_use_case,
    get_registrar_usuario_use_case,
    get_actualizar_usuario_use_case,
    get_eliminar_usuario_use_case,
)
from tests.factories.usuario_factory import crear_usuario_mock, crear_usuario_admin_mock
from tests.factories.auth_factory import crear_token_mock, headers_auth, sesion_viva


@pytest.fixture
def mock_repositorio_usuarios():
    return MagicMock(spec=RepositorioUsuarios)


@pytest.fixture
def mock_auth_service():
    service = MagicMock(spec=AuthenticationService)
    service.hash_password.return_value = "hashed_password_123"
    service.verificar_password.return_value = True
    service.crear_access_token.return_value = "mock_jwt_token"
    return service


@pytest.fixture
def usuario_autenticado():
    return crear_usuario_admin_mock()


@pytest.fixture
def token_valido():
    return crear_token_mock()


@pytest.fixture
def headers_auth_validos(token_valido):
    return headers_auth(token_valido)


@pytest.fixture
def client(usuario_autenticado, mock_repositorio_usuarios, mock_auth_service):
    from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
    from app.aplicacion.usuario.use_cases.obtener_usuarios import ObtenerUsuariosUseCase
    from app.aplicacion.usuario.use_cases.registrar_usuario import RegistrarUsuarioUseCase
    from app.aplicacion.usuario.use_cases.actualizar_usuario import ActualizarUsuarioUseCase
    from app.aplicacion.usuario.use_cases.eliminar_usuario import EliminarUsuarioUseCase
    from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase

    def override_get_current_user():
        return usuario_autenticado

    def override_get_audit_service():
        # Los eventos críticos escriben fail-closed: sin la tabla de auditoría
        # levantada, un 403 real se convertiría en 500. Estos tests miden
        # autorización, no persistencia de auditoría, así que se aísla.
        servicio = MagicMock(spec=AuditService)
        servicio.con_usuario.side_effect = lambda scope, rut, id_sesion=None: scope
        return servicio

    def override_get_repositorio_sesiones():
        repo = MagicMock(spec=RepositorioSesiones)
        repo.obtener_por_id.side_effect = lambda id_sesion, conn=None: sesion_viva(id_sesion)
        return repo

    def override_get_obtener_usuario_use_case():
        uc = MagicMock(spec=ObtenerUsuarioUseCase)
        uc.ejecutar.return_value = usuario_autenticado
        return uc

    def override_get_obtener_usuarios_use_case():
        uc = MagicMock(spec=ObtenerUsuariosUseCase)
        uc.ejecutar.return_value = [usuario_autenticado]
        uc.ejecutar_paginado.return_value = ([usuario_autenticado], 1)
        return uc

    def override_get_registrar_usuario_use_case():
        uc = MagicMock(spec=RegistrarUsuarioUseCase)
        uc.ejecutar.return_value = True
        return uc

    def override_get_actualizar_usuario_use_case():
        uc = MagicMock(spec=ActualizarUsuarioUseCase)
        uc.ejecutar.return_value = True
        return uc

    def override_get_eliminar_usuario_use_case():
        uc = MagicMock(spec=EliminarUsuarioUseCase)
        return uc

    def override_get_iniciar_sesion_use_case():
        uc = MagicMock(spec=IniciarSesionUseCase)
        from app.aplicacion.auth.dtos.iniciar_sesion_response_dto import IniciarSesionResponseDTO
        uc.execute.return_value = IniciarSesionResponseDTO(
            access_token="mock_jwt_token",
            usuario=usuario_autenticado,
            expire_minutes=60,
        )
        return uc

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_audit_service] = override_get_audit_service
    app.dependency_overrides[get_repositorio_sesiones_dep] = override_get_repositorio_sesiones
    app.dependency_overrides[get_obtener_usuario_use_case] = override_get_obtener_usuario_use_case
    app.dependency_overrides[get_obtener_usuarios_use_case] = override_get_obtener_usuarios_use_case
    app.dependency_overrides[get_registrar_usuario_use_case] = override_get_registrar_usuario_use_case
    app.dependency_overrides[get_actualizar_usuario_use_case] = override_get_actualizar_usuario_use_case
    app.dependency_overrides[get_eliminar_usuario_use_case] = override_get_eliminar_usuario_use_case
    app.dependency_overrides[get_iniciar_sesion_use_case] = override_get_iniciar_sesion_use_case

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
