import pytest
from unittest.mock import MagicMock

from app.main import app
from app.dominio.usuario.usuario import Usuario
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.recordatorio.dependencias.deps import (
    get_obtener_recordatorios_usuario_use_case,
)
from app.aplicacion.recordatorio.use_cases.obtener_recordatorios import ObtenerRecordatoriosUsuarioUseCase
from tests.factories.usuario_factory import crear_usuario_admin_mock
from tests.factories.auth_factory import crear_token_mock, headers_auth
from tests.factories.recordatorio_factory import crear_recordatorio_usuario_mock


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
def client(usuario_autenticado):
    def override_get_current_user():
        return usuario_autenticado

    def override_get_obtener_recordatorios_usuario_use_case():
        uc = MagicMock(spec=ObtenerRecordatoriosUsuarioUseCase)
        uc.ejecutar_paginado.return_value = (
            [crear_recordatorio_usuario_mock(id=1), crear_recordatorio_usuario_mock(id=2)],
            2,
        )
        return uc

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_recordatorios_usuario_use_case] = (
        override_get_obtener_recordatorios_usuario_use_case
    )

    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestRecordatorioEndpointsPaginacion:

    def test_obtener_recordatorios_estructura_paginada(self, client, headers_auth_validos):
        response = client.get(
            "/recordatorios/",
            params={"fecha": "2026-09-01"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "pagina" in data
        assert "tamano_pagina" in data
        assert "total_paginas" in data
        assert isinstance(data["data"], list)
        assert data["total"] == 2
        assert data["pagina"] == 1
        assert data["tamano_pagina"] == 15
        assert data["total_paginas"] == 1

    def test_obtener_recordatorios_pagina_default(self, client, headers_auth_validos):
        response = client.get(
            "/recordatorios/",
            params={"fecha": "2026-09-01"},
            headers=headers_auth_validos,
        )

        data = response.json()
        assert data["pagina"] == 1
        assert data["tamano_pagina"] == 15

    def test_obtener_recordatorios_pagina_2(self, client, headers_auth_validos):
        response = client.get(
            "/recordatorios/",
            params={"fecha": "2026-09-01", "pagina": 2},
            headers=headers_auth_validos,
        )

        data = response.json()
        assert data["pagina"] == 2

    def test_obtener_recordatorios_tamano_personalizado(self, client, headers_auth_validos):
        response = client.get(
            "/recordatorios/",
            params={"fecha": "2026-09-01", "tamano_pagina": 5},
            headers=headers_auth_validos,
        )

        data = response.json()
        assert data["tamano_pagina"] == 5

    def test_obtener_recordatorios_total_paginas(self, client, headers_auth_validos):
        from app.main import app as real_app
        from starlette.testclient import TestClient

        def override_get_current_user():
            return crear_usuario_admin_mock()

        def override_get_obtener_recordatorios_usuario_use_case():
            uc = MagicMock(spec=ObtenerRecordatoriosUsuarioUseCase)
            uc.ejecutar_paginado.return_value = (
                [crear_recordatorio_usuario_mock(id=i) for i in range(1, 16)],
                30,
            )
            return uc

        real_app.dependency_overrides[get_current_user] = override_get_current_user
        real_app.dependency_overrides[get_obtener_recordatorios_usuario_use_case] = (
            override_get_obtener_recordatorios_usuario_use_case
        )

        with TestClient(real_app) as c:
            response = c.get(
                "/recordatorios/",
                params={"fecha": "2026-09-01", "tamano_pagina": 15},
                headers=headers_auth_validos,
            )

        data = response.json()
        assert data["total"] == 30
        assert data["total_paginas"] == 2

    def test_obtener_recordatorios_sin_fecha(self, client, headers_auth_validos):
        response = client.get(
            "/recordatorios/",
            headers=headers_auth_validos,
        )

        assert response.status_code == 422

    def test_obtener_recordatorios_fecha_invalida(self, client, headers_auth_validos):
        response = client.get(
            "/recordatorios/",
            params={"fecha": "fecha-invalida"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 400
