import pytest
from unittest.mock import MagicMock

from app.aplicacion.cobranza.use_cases.obtener_dashboard_cobranza import (
    ObtenerDashboardCobranzaUseCase,
)
from app.dominio.usuario.usuario import Usuario
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.cobranza.dependencias.deps import (
    get_obtener_dashboard_cobranza_use_case,
)
from tests.factories.auth_factory import crear_token_mock, headers_auth
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
def headers_auth_validos():
    return headers_auth(crear_token_mock())


@pytest.fixture
def use_case_dashboard_mock():
    mock = MagicMock(spec=ObtenerDashboardCobranzaUseCase)
    mock.ejecutar.return_value = {
        'kpis': {},
        'pagados': [],
        'morosos': [],
        'atrasados': [],
        'sin_plan_pago': [],
        'llamar_hoy': [],
        'proximos10': [],
    }
    return mock


@pytest.fixture
def usuario_holder():
    return {"usuario": _usuario_con_permiso("VER_COBRANZA_PROPIOS")}


@pytest.fixture
def client(usuario_holder, use_case_dashboard_mock):
    def override_get_current_user():
        return usuario_holder["usuario"]

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_dashboard_cobranza_use_case] = (
        lambda: use_case_dashboard_mock
    )

    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestDashboardCobranza:

    def test_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_dashboard_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.get("/cobranza/dashboard", headers=headers_auth_validos)

        assert response.status_code == 403
        use_case_dashboard_mock.ejecutar.assert_not_called()

    def test_con_ver_propios_scoping_al_propio_rut(self, client, headers_auth_validos, use_case_dashboard_mock):
        response = client.get("/cobranza/dashboard", headers=headers_auth_validos)

        assert response.status_code == 200
        use_case_dashboard_mock.ejecutar.assert_called_once_with("11111111-1")

    def test_con_ver_todos_dashboard_global(self, client, headers_auth_validos, use_case_dashboard_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_COBRANZA_TODOS")

        response = client.get("/cobranza/dashboard", headers=headers_auth_validos)

        assert response.status_code == 200
        use_case_dashboard_mock.ejecutar.assert_called_once_with(None)

    def test_con_ambos_permisos_gana_el_global(self, client, headers_auth_validos, use_case_dashboard_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_COBRANZA_PROPIOS", "VER_COBRANZA_TODOS")

        response = client.get("/cobranza/dashboard", headers=headers_auth_validos)

        assert response.status_code == 200
        use_case_dashboard_mock.ejecutar.assert_called_once_with(None)
