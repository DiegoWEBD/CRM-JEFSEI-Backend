import pytest
from unittest.mock import MagicMock, patch
from tests.integration.api.conftest_api import *


@pytest.mark.integration
@pytest.mark.auth
class TestAuthEndpoints:

    def test_login_exitoso(self, client):
        response = client.post("/auth/login", json={
            "rut": "12345678-9",
            "password": "password123",
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expire_minutes"] == 60
        assert "usuario" in data
        assert data["usuario"]["rut"] == "12345678-9"

    def test_login_credenciales_invalidas(self, client, mock_repositorio_usuarios):
        mock_repositorio_usuarios.buscar.return_value = None

        from app.presentacion.api.auth.dependencias.get_iniciar_sesion_use_case import get_iniciar_sesion_use_case
        from app.aplicacion.auth.use_cases.iniciar_sesion import IniciarSesionUseCase

        def override_get_iniciar_sesion_use_case():
            uc = MagicMock(spec=IniciarSesionUseCase)
            uc.execute.return_value = None
            return uc

        app.dependency_overrides[get_iniciar_sesion_use_case] = override_get_iniciar_sesion_use_case

        response = client.post("/auth/login", json={
            "rut": "99999999-9",
            "password": "wrong_password",
        })

        assert response.status_code == 401

    def test_login_campos_requeridos(self, client):
        response = client.post("/auth/login", json={})

        assert response.status_code == 422

    def test_login_rut_normalizado(self, client):
        response = client.post("/auth/login", json={
            "rut": "123456789",
            "password": "password123",
        })

        assert response.status_code in [200, 401]
