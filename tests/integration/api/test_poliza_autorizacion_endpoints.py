from unittest.mock import MagicMock

import pytest

from app.aplicacion.plan_pago.use_cases.crear_plan_pago import CrearPlanPagoUseCase
from app.aplicacion.poliza.use_cases.cancelar_poliza import CancelarPolizaUseCase
from app.aplicacion.poliza.use_cases.reactivar_poliza import ReactivarPolizaUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.usuario.usuario import Usuario
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.plan_pago.dependencias.deps import get_crear_plan_pago_use_case
from app.presentacion.api.poliza.dependencias.deps import (
    get_cancelar_poliza_use_case,
    get_reactivar_poliza_use_case,
)
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock


def _usuario_con_permisos(*codigos: str) -> Usuario:
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


BODY_PLAN_PAGO = {
    'numero_cuotas': 3,
    'fecha_primera_cuota': '2026-03-01T00:00:00',
}


def _client(usuario, use_case_mock, provider):
    def override_get_current_user():
        return usuario

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[provider] = lambda: use_case_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestCancelarReactivarPolizaEndpoint:

    @pytest.fixture
    def use_case_mock(self):
        return MagicMock(spec=CancelarPolizaUseCase)

    @pytest.fixture
    def client_con_permiso(self, use_case_mock):
        usuario = _usuario_con_permisos('CANCELAR_POLIZA_TODOS')
        yield from _client(usuario, use_case_mock, get_cancelar_poliza_use_case)

    @pytest.fixture
    def client_sin_permiso(self, use_case_mock):
        usuario = _usuario_con_permisos('OBTENER_POLIZAS_PROPIAS')
        yield from _client(usuario, use_case_mock, get_cancelar_poliza_use_case)

    def test_sin_permiso_retorna_403(self, client_sin_permiso, use_case_mock, headers_auth_validos):
        response = client_sin_permiso.post('/polizas/POL-001/cancelar', headers=headers_auth_validos)

        assert response.status_code == 403
        use_case_mock.ejecutar.assert_not_called()

    def test_poliza_denegada_retorna_404_identico_al_inexistente(
        self, client_con_permiso, use_case_mock, headers_auth_validos
    ):
        use_case_mock.ejecutar.side_effect = RecursoNoEncontradoException(
            'Póliza POL-001 no encontrada'
        )

        response = client_con_permiso.post('/polizas/POL-001/cancelar', headers=headers_auth_validos)

        assert response.status_code == 404
        assert response.json()['detail'] == 'Póliza POL-001 no encontrada'

    def test_cancelar_exitoso_retorna_200(self, client_con_permiso, use_case_mock, headers_auth_validos):
        use_case_mock.ejecutar.return_value = None

        response = client_con_permiso.post('/polizas/POL-001/cancelar', headers=headers_auth_validos)

        assert response.status_code == 200
        use_case_mock.ejecutar.assert_called_once()

    @pytest.fixture
    def reactivar_use_case_mock(self):
        return MagicMock(spec=ReactivarPolizaUseCase)

    @pytest.fixture
    def client_reactivar_con_permiso(self, reactivar_use_case_mock):
        usuario = _usuario_con_permisos('REACTIVAR_POLIZA_PROPIOS')
        yield from _client(usuario, reactivar_use_case_mock, get_reactivar_poliza_use_case)

    def test_reactivar_exitoso_retorna_200(
        self, client_reactivar_con_permiso, reactivar_use_case_mock, headers_auth_validos
    ):
        reactivar_use_case_mock.ejecutar.return_value = None

        response = client_reactivar_con_permiso.post(
            '/polizas/POL-001/reactivar', headers=headers_auth_validos
        )

        assert response.status_code == 200
        reactivar_use_case_mock.ejecutar.assert_called_once()


@pytest.mark.integration
class TestCrearPlanPagoEndpoint:

    @pytest.fixture
    def use_case_mock(self):
        return MagicMock(spec=CrearPlanPagoUseCase)

    @pytest.fixture
    def client_con_permiso(self, use_case_mock):
        usuario = _usuario_con_permisos('CREAR_PLAN_PAGO_GLOBAL')
        yield from _client(usuario, use_case_mock, get_crear_plan_pago_use_case)

    @pytest.fixture
    def client_solo_vista(self, use_case_mock):
        # La vista VER_PLAN_PAGO_* ya no habilita crear el plan de pago.
        usuario = _usuario_con_permisos('VER_PLAN_PAGO_GLOBAL')
        yield from _client(usuario, use_case_mock, get_crear_plan_pago_use_case)

    def test_solo_permiso_de_vista_retorna_403(
        self, client_solo_vista, use_case_mock, headers_auth_validos
    ):
        response = client_solo_vista.post(
            '/polizas/POL-001/plan-pago', json=BODY_PLAN_PAGO, headers=headers_auth_validos
        )

        assert response.status_code == 403
        use_case_mock.ejecutar.assert_not_called()

    def test_denegacion_retorna_404_identico_al_inexistente(
        self, client_con_permiso, use_case_mock, headers_auth_validos
    ):
        use_case_mock.ejecutar.side_effect = RecursoNoEncontradoException(
            'Póliza POL-001 no encontrada'
        )

        response = client_con_permiso.post(
            '/polizas/POL-001/plan-pago', json=BODY_PLAN_PAGO, headers=headers_auth_validos
        )

        assert response.status_code == 404
        assert response.json()['detail'] == 'Póliza POL-001 no encontrada'

    def test_creacion_exitosa_retorna_201(
        self, client_con_permiso, use_case_mock, headers_auth_validos
    ):
        use_case_mock.ejecutar.return_value = None

        response = client_con_permiso.post(
            '/polizas/POL-001/plan-pago', json=BODY_PLAN_PAGO, headers=headers_auth_validos
        )

        assert response.status_code == 201
        use_case_mock.ejecutar.assert_called_once()
