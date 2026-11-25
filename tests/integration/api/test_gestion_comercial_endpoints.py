import pytest
from unittest.mock import MagicMock

from app.aplicacion.gestion_comercial.use_cases.obtener_gestiones_comerciales import ObtenerGestionesComercialesUseCase
from app.aplicacion.gestion_comercial.use_cases.obtener_ultima_gestion_comercial import ObtenerUltimaGestionComercialUseCase
from app.aplicacion.gestion_comercial.use_cases.registrar_gestion_comercial import RegistrarGestionComercialUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.gestion_comercial.dependencias.deps import (
    get_obtener_gestiones_comerciales_use_case,
    get_obtener_ultima_gestion_comercial_use_case,
    get_registrar_gestion_comercial_use_case,
)
from tests.factories.auth_factory import crear_token_mock, headers_auth
from tests.factories.gestion_comercial_factory import crear_gestion_comercial_mock
from tests.factories.usuario_factory import (
    crear_permiso_mock,
    crear_rol_mock,
    crear_usuario_mock,
)


def _usuario_con_permiso(*codigos_permiso: str) -> Usuario:
    return crear_usuario_mock(
        rut="11111111-1",
        roles=[crear_rol_mock(permisos=[crear_permiso_mock(codigo=codigo) for codigo in codigos_permiso])],
    )


@pytest.fixture
def token_valido():
    return crear_token_mock()


@pytest.fixture
def headers_auth_validos(token_valido):
    return headers_auth(token_valido)


@pytest.fixture
def use_case_registrar_mock():
    mock = MagicMock(spec=RegistrarGestionComercialUseCase)
    mock.ejecutar.return_value = crear_gestion_comercial_mock()
    return mock


@pytest.fixture
def use_case_obtener_mock():
    mock = MagicMock(spec=ObtenerGestionesComercialesUseCase)
    mock.ejecutar.return_value = [crear_gestion_comercial_mock()]
    return mock


@pytest.fixture
def use_case_ultima_mock():
    mock = MagicMock(spec=ObtenerUltimaGestionComercialUseCase)
    mock.ejecutar.return_value = crear_gestion_comercial_mock()
    return mock


@pytest.fixture
def usuario_holder():
    return {"usuario": _usuario_con_permiso("REGISTRAR_GESTION_COMERCIAL_PROPIOS")}


@pytest.fixture
def client(
    usuario_holder,
    use_case_registrar_mock,
    use_case_obtener_mock,
    use_case_ultima_mock,
):
    def override_get_current_user():
        return usuario_holder["usuario"]

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_registrar_gestion_comercial_use_case] = lambda: use_case_registrar_mock
    app.dependency_overrides[get_obtener_gestiones_comerciales_use_case] = lambda: use_case_obtener_mock
    app.dependency_overrides[get_obtener_ultima_gestion_comercial_use_case] = lambda: use_case_ultima_mock

    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _payload_registrar(**kwargs):
    payload = {
        "tipo": "llamada",
        "id_prospecto": 7,
        "titulo": "Contacto inicial",
        "estado_contacto": None,
        "observacion": None,
        "fecha_gestion": "2026-11-20T10:00:00",
    }
    payload.update(kwargs)
    return payload


@pytest.mark.integration
class TestGestionComercialRegistrar:

    def test_registrar_pasa_usuario_del_token(self, client, headers_auth_validos, use_case_registrar_mock):
        response = client.post(
            "/gestiones-comerciales/",
            json=_payload_registrar(),
            headers=headers_auth_validos,
        )

        assert response.status_code == 201
        kwargs = use_case_registrar_mock.ejecutar.call_args.kwargs
        assert kwargs["usuario"].rut == "11111111-1"
        assert kwargs["id_prospecto"] == 7
        # La atribución viene del token: no se acepta rut_usuario del cliente.
        assert "rut_usuario" not in kwargs

    def test_registrar_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_registrar_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.post(
            "/gestiones-comerciales/",
            json=_payload_registrar(),
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_registrar_mock.ejecutar.assert_not_called()

    def test_registrar_prospecto_ajeno_retorna_403(self, client, headers_auth_validos, use_case_registrar_mock):
        use_case_registrar_mock.ejecutar.side_effect = UsuarioNoAutorizadoException()

        response = client.post(
            "/gestiones-comerciales/",
            json=_payload_registrar(),
            headers=headers_auth_validos,
        )

        assert response.status_code == 403

    def test_registrar_prospecto_inexistente_retorna_404(self, client, headers_auth_validos, use_case_registrar_mock):
        use_case_registrar_mock.ejecutar.side_effect = RecursoNoEncontradoException("El prospecto no existe")

        response = client.post(
            "/gestiones-comerciales/",
            json=_payload_registrar(id_prospecto=999),
            headers=headers_auth_validos,
        )

        assert response.status_code == 404


@pytest.mark.integration
class TestGestionComercialLectura:

    def test_obtener_gestiones_pasa_usuario(self, client, headers_auth_validos, use_case_obtener_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_GESTIONES_COMERCIALES_PROPIOS")

        response = client.get(
            "/gestiones-comerciales/",
            params={"id_prospecto": 7},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = use_case_obtener_mock.ejecutar.call_args.kwargs
        assert kwargs["usuario"].rut == "11111111-1"
        assert kwargs["id_prospecto"] == 7

    def test_obtener_gestiones_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_obtener_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.get(
            "/gestiones-comerciales/",
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_obtener_mock.ejecutar.assert_not_called()

    def test_obtener_gestiones_prospecto_ajeno_retorna_403(self, client, headers_auth_validos, use_case_obtener_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_GESTIONES_COMERCIALES_PROPIOS")
        use_case_obtener_mock.ejecutar.side_effect = UsuarioNoAutorizadoException()

        response = client.get(
            "/gestiones-comerciales/",
            params={"id_prospecto": 7},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403

    def test_obtener_ultima_pasa_usuario(self, client, headers_auth_validos, use_case_ultima_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_GESTIONES_COMERCIALES_TODOS")

        response = client.get(
            "/gestiones-comerciales/final",
            params={"id_prospecto": 7},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = use_case_ultima_mock.ejecutar.call_args.kwargs
        assert kwargs["usuario"].rut == "11111111-1"
        assert kwargs["id_prospecto"] == 7

    def test_obtener_ultima_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_ultima_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.get(
            "/gestiones-comerciales/final",
            params={"id_prospecto": 7},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_ultima_mock.ejecutar.assert_not_called()

    def test_obtener_ultima_prospecto_ajeno_retorna_403(self, client, headers_auth_validos, use_case_ultima_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_GESTIONES_COMERCIALES_PROPIOS")
        use_case_ultima_mock.ejecutar.side_effect = UsuarioNoAutorizadoException()

        response = client.get(
            "/gestiones-comerciales/final",
            params={"id_prospecto": 7},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
