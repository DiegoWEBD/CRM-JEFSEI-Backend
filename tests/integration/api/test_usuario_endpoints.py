import pytest
from unittest.mock import MagicMock, patch
from tests.integration.api.conftest_api import *


@pytest.mark.integration
class TestUsuarioEndpoints:

    def test_obtener_usuarios(self, client, headers_auth_validos):
        response = client.get("/usuarios/", headers=headers_auth_validos)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    def test_obtener_usuario_por_rut(self, client, headers_auth_validos):
        response = client.get("/usuarios/12345678-9", headers=headers_auth_validos)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["rut"] == "12345678-9"

    def test_registrar_usuario(self, client, headers_auth_validos):
        response = client.post("/usuarios/", json={
            "rut": "11111111-1",
            "nombre": "María López",
            "correo": "maria@test.com",
            "telefono": "+56911111111",
            "id_sucursal": 1,
            "password": "password123",
            "meta_mensual_uf": 100,
            "codigo_roles": ["EJECUTIVO"],
            "porcentaje_comision": 0.05,
        }, headers=headers_auth_validos)

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Usuario registrado correctamente"

    def test_registrar_usuario_datos_invalidos(self, client, headers_auth_validos):
        response = client.post("/usuarios/", json={
            "rut": "11111111-1",
        }, headers=headers_auth_validos)

        assert response.status_code == 422

    def test_actualizar_usuario(self, client, headers_auth_validos):
        response = client.put("/usuarios/12345678-9", json={
            "rut": "12345678-9",
            "nombre": "Juan Pérez Actualizado",
            "correo": "juan@test.com",
            "telefono": "+56912345678",
            "id_sucursal": 1,
            "password": None,
            "meta_mensual_uf": 200,
            "codigo_roles": ["ADMIN"],
            "porcentaje_comision": 0.10,
            "habilitado": True,
        }, headers=headers_auth_validos)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Usuario actualizado correctamente"

    def test_eliminar_usuario(self, client, headers_auth_validos):
        response = client.delete("/usuarios/12345678-9", headers=headers_auth_validos)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Usuario eliminado correctamente"

    def test_obtener_usuario_no_autenticado(self):
        from app.main import app as real_app
        from starlette.testclient import TestClient

        real_app.dependency_overrides.clear()
        with TestClient(real_app) as c:
            response = c.get("/usuarios/")

        assert response.status_code == 401

    def test_obtener_usuario_sin_permiso(self, client, mock_repositorio_usuarios):
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
            response = c.get("/usuarios/")

        assert response.status_code == 403
