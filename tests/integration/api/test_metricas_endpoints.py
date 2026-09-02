import pytest
from unittest.mock import MagicMock, patch
from tests.integration.api.conftest_api import *


@pytest.mark.integration
class TestMetricasEndpoints:

    def test_kpis_comerciales(self, client, headers_auth_validos):
        from app.presentacion.api.metricas.dependencias.deps import get_obtener_kpis_comerciales_use_case

        def override_get_kpis():
            uc = MagicMock()
            uc.ejecutar.return_value = {
                "prima_neta": 50000,
                "tasa_cierre": 0.35,
                "tasa_renovacion": 0.80,
            }
            return uc

        app.dependency_overrides[get_obtener_kpis_comerciales_use_case] = override_get_kpis

        from starlette.testclient import TestClient
        with TestClient(app) as c:
            response = c.get("/metricas/kpis-comerciales", headers=headers_auth_validos)

        assert response.status_code == 200

    def test_metricas_sin_permiso(self, client):
        from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
        from tests.factories.usuario_factory import crear_usuario_mock, crear_rol_mock, crear_permiso_mock

        permisos_vacios = []
        rol_sin_permisos = crear_rol_mock(permisos=permisos_vacios)
        usuario_sin_permiso = crear_usuario_mock(roles=[rol_sin_permisos])

        def override_get_current_user():
            return usuario_sin_permiso

        app.dependency_overrides[get_current_user] = override_get_current_user

        from starlette.testclient import TestClient
        with TestClient(app) as c:
            response = c.get("/metricas/kpis-comerciales")

        assert response.status_code == 403
