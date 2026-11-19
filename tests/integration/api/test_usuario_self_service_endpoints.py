import pytest
from unittest.mock import MagicMock
from tests.integration.api.conftest_api import *


def _usuario_sin_permisos(rut: str = "12345678-9"):
    from tests.factories.usuario_factory import crear_usuario_mock, crear_rol_mock

    return crear_usuario_mock(rut=rut, roles=[crear_rol_mock(permisos=[])])


@pytest.mark.integration
class TestUsuariosVisibilidadPerfil:

    def test_obtener_usuario_propio_sin_permisos_es_permitido(self, client):
        from app.main import app
        from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
        from starlette.testclient import TestClient

        usuario = _usuario_sin_permisos()
        app.dependency_overrides[get_current_user] = lambda: usuario

        with TestClient(app) as c:
            response = c.get("/usuarios/12345678-9")

        assert response.status_code == 200
        assert response.json()["data"]["rut"] == "12345678-9"

    def test_obtener_usuario_ajeno_sin_permisos_es_rechazado(self, client):
        from app.main import app
        from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
        from starlette.testclient import TestClient

        usuario = _usuario_sin_permisos()
        app.dependency_overrides[get_current_user] = lambda: usuario

        with TestClient(app) as c:
            response = c.get("/usuarios/99999999-9")

        assert response.status_code == 403

    def test_obtener_usuario_ajeno_con_obtener_usuarios_es_permitido(self, client, headers_auth_validos):
        # El usuario autenticado del fixture es admin (tiene OBTENER_USUARIOS)
        response = client.get("/usuarios/99999999-9", headers=headers_auth_validos)

        assert response.status_code == 200


@pytest.mark.integration
class TestActualizarPerfilSelfService:

    def test_actualizar_perfil_propio(self, client, headers_auth_validos):
        response = client.patch("/usuarios/12345678-9", json={
            "nombre": "Nombre Actualizado",
        }, headers=headers_auth_validos)

        assert response.status_code == 200
        assert response.json()["message"] == "Perfil actualizado correctamente"

    def test_actualizar_perfil_ajeno_es_rechazado(self, client, headers_auth_validos):
        # Incluso con ADMINISTRAR_USUARIOS, el PATCH es solo self-service
        response = client.patch("/usuarios/99999999-9", json={
            "nombre": "Nombre De Otro",
        }, headers=headers_auth_validos)

        assert response.status_code == 403
        assert "propio perfil" in response.json()["detail"]

    def test_actualizar_perfil_nombre_invalido(self, client, headers_auth_validos):
        response = client.patch("/usuarios/12345678-9", json={
            "nombre": "A",
        }, headers=headers_auth_validos)

        assert response.status_code == 400

    def test_actualizar_perfil_datos_incompletos(self, client, headers_auth_validos):
        response = client.patch("/usuarios/12345678-9", json={}, headers=headers_auth_validos)

        assert response.status_code == 422


@pytest.mark.integration
class TestCambiarPasswordSelfService:

    def test_cambiar_password_propio(self, client, headers_auth_validos):
        response = client.put("/usuarios/12345678-9/password", json={
            "password_actual": "PasswordActual1",
            "password_nueva": "PasswordNueva1",
        }, headers=headers_auth_validos)

        assert response.status_code == 200
        assert response.json()["message"] == "Contraseña actualizada correctamente"

    def test_cambiar_password_ajeno_es_rechazado(self, client, headers_auth_validos):
        response = client.put("/usuarios/99999999-9/password", json={
            "password_actual": "PasswordActual1",
            "password_nueva": "PasswordNueva1",
        }, headers=headers_auth_validos)

        assert response.status_code == 403
        assert "propia contraseña" in response.json()["detail"]

    def test_cambiar_password_nueva_debil(self, client, headers_auth_validos):
        response = client.put("/usuarios/12345678-9/password", json={
            "password_actual": "PasswordActual1",
            "password_nueva": "corta",
        }, headers=headers_auth_validos)

        assert response.status_code == 400
        assert "al menos 12 caracteres" in response.json()["detail"]

    def test_cambiar_password_datos_incompletos(self, client, headers_auth_validos):
        response = client.put("/usuarios/12345678-9/password", json={
            "password_actual": "PasswordActual1",
        }, headers=headers_auth_validos)

        assert response.status_code == 422
