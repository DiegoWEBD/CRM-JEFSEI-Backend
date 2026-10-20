from unittest.mock import MagicMock

import pytest
from app.main import app
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.evaluacion_proyectos.use_cases.subir_estudio_comercial import SubirEstudioComercialUseCase
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.cotizacion.dependencias.deps import get_subir_estudio_comercial_use_case
from app.presentacion.api.estudio_comercial.deps import get_repositorio_estudios
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import get_authorization_service
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock
from tests.factories.auth_factory import crear_token_mock, headers_auth


PDF_MOCK = b'%PDF-1.4\n%contenido de prueba\n'


def _usuario_con_permisos(*codigos: str) -> Usuario:
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


@pytest.fixture
def usuario_subir():
    return _usuario_con_permisos('SUBIR_ESTUDIO_COMERCIAL')


@pytest.fixture
def usuario_ver_propios():
    return _usuario_con_permisos('VER_ESTUDIOS_COMERCIALES_PROPIOS')


@pytest.fixture
def usuario_ver_todos():
    return _usuario_con_permisos('VER_ESTUDIOS_COMERCIALES_TODOS')


@pytest.fixture
def usuario_sin_permisos():
    return _usuario_con_permisos('OBTENER_PROSPECTOS_TODOS')


@pytest.fixture
def use_case_subir_mock():
    return MagicMock(spec=SubirEstudioComercialUseCase)


@pytest.fixture
def authorization_service_mock():
    service = MagicMock(spec=AuthorizationService)
    service.usuario_puede_ver_estudios_comerciales.return_value = False
    service.usuario_puede_descargar_estudio_comercial.return_value = False
    return service


@pytest.fixture
def repositorio_estudios_mock():
    repositorio = MagicMock()
    repositorio.listar_por_id_solicitud.return_value = []
    return repositorio


@pytest.fixture
def client_subir(usuario_subir, use_case_subir_mock):
    def override_get_current_user():
        return usuario_subir

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_subir_estudio_comercial_use_case] = lambda: use_case_subir_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_subir_sin_permiso(usuario_sin_permisos, use_case_subir_mock):
    def override_get_current_user():
        return usuario_sin_permisos

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_subir_estudio_comercial_use_case] = lambda: use_case_subir_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_ver_propios(usuario_ver_propios, authorization_service_mock, repositorio_estudios_mock):
    def override_get_current_user():
        return usuario_ver_propios

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_authorization_service] = lambda: authorization_service_mock
    app.dependency_overrides[get_repositorio_estudios] = lambda: repositorio_estudios_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_ver_todos(usuario_ver_todos, authorization_service_mock, repositorio_estudios_mock):
    def override_get_current_user():
        return usuario_ver_todos

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_authorization_service] = lambda: authorization_service_mock
    app.dependency_overrides[get_repositorio_estudios] = lambda: repositorio_estudios_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_ver_sin_permiso(usuario_sin_permisos, authorization_service_mock, repositorio_estudios_mock):
    def override_get_current_user():
        return usuario_sin_permisos

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_authorization_service] = lambda: authorization_service_mock
    app.dependency_overrides[get_repositorio_estudios] = lambda: repositorio_estudios_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestSubirEstudioComercialEndpoint:

    @pytest.mark.auth
    def test_subir_estudio_ajeno_retorna_403(self, client_subir, use_case_subir_mock, headers_auth_validos):
        use_case_subir_mock.ejecutar.side_effect = UsuarioNoAutorizadoException

        response = client_subir.post(
            '/solicitudes-cotizacion/1/estudios-comerciales',
            files={'archivo': ('estudio.pdf', PDF_MOCK, 'application/pdf')},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_subir_mock.ejecutar.assert_called_once()

    @pytest.mark.auth
    def test_sin_permiso_subir_retorna_403(self, client_subir_sin_permiso, use_case_subir_mock, headers_auth_validos):
        response = client_subir_sin_permiso.post(
            '/solicitudes-cotizacion/1/estudios-comerciales',
            files={'archivo': ('estudio.pdf', PDF_MOCK, 'application/pdf')},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_subir_mock.ejecutar.assert_not_called()

    def test_subir_estudio_propio_retorna_201(self, client_subir, use_case_subir_mock, headers_auth_validos):
        use_case_subir_mock.ejecutar.return_value = (7, 'estudio_comercial_1_123.pdf')

        response = client_subir.post(
            '/solicitudes-cotizacion/1/estudios-comerciales',
            files={'archivo': ('estudio.pdf', PDF_MOCK, 'application/pdf')},
            headers=headers_auth_validos,
        )

        assert response.status_code == 201
        assert response.json()['id'] == 7


@pytest.mark.integration
class TestListarEstudiosComercialesEndpoint:

    @pytest.mark.auth
    def test_estudios_ajenos_con_permisos_propios_retorna_403(
        self, client_ver_propios, authorization_service_mock, repositorio_estudios_mock, headers_auth_validos
    ):
        authorization_service_mock.usuario_puede_ver_estudios_comerciales.return_value = False

        response = client_ver_propios.get(
            '/solicitudes-cotizacion/1/estudios-comerciales',
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        repositorio_estudios_mock.listar_por_id_solicitud.assert_not_called()

    def test_estudios_propios_retorna_200(
        self, client_ver_propios, authorization_service_mock, repositorio_estudios_mock, headers_auth_validos
    ):
        authorization_service_mock.usuario_puede_ver_estudios_comerciales.return_value = True
        estudio = MagicMock()
        estudio.id = 5
        estudio.nombre_archivo = 'estudio_comercial_1_123.pdf'
        repositorio_estudios_mock.listar_por_id_solicitud.return_value = [estudio]

        response = client_ver_propios.get(
            '/solicitudes-cotizacion/1/estudios-comerciales',
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        assert response.json() == [{'id': 5, 'nombre_archivo': 'estudio_comercial_1_123.pdf'}]

    @pytest.mark.auth
    def test_sin_permiso_retorna_403(self, client_ver_sin_permiso, repositorio_estudios_mock, headers_auth_validos):
        response = client_ver_sin_permiso.get(
            '/solicitudes-cotizacion/1/estudios-comerciales',
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        repositorio_estudios_mock.listar_por_id_solicitud.assert_not_called()


@pytest.mark.integration
class TestDescargarEstudioComercialEndpoint:

    @pytest.mark.auth
    def test_archivo_ajeno_retorna_403(
        self, client_ver_propios, authorization_service_mock, repositorio_estudios_mock, headers_auth_validos
    ):
        authorization_service_mock.usuario_puede_descargar_estudio_comercial.return_value = False

        response = client_ver_propios.get(
            '/solicitudes-cotizacion/1/estudios-comerciales/5/archivo',
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        repositorio_estudios_mock.listar_por_id_solicitud.assert_not_called()

    def test_estudio_no_pertenece_a_solicitud_retorna_404(
        self, client_ver_propios, authorization_service_mock, repositorio_estudios_mock, headers_auth_validos
    ):
        authorization_service_mock.usuario_puede_descargar_estudio_comercial.return_value = True
        repositorio_estudios_mock.listar_por_id_solicitud.return_value = []

        response = client_ver_propios.get(
            '/solicitudes-cotizacion/1/estudios-comerciales/5/archivo',
            headers=headers_auth_validos,
        )

        assert response.status_code == 404

    @pytest.mark.auth
    def test_sin_permiso_retorna_403(self, client_ver_sin_permiso, repositorio_estudios_mock, headers_auth_validos):
        response = client_ver_sin_permiso.get(
            '/solicitudes-cotizacion/1/estudios-comerciales/5/archivo',
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        repositorio_estudios_mock.listar_por_id_solicitud.assert_not_called()
