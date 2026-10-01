from datetime import time
from unittest.mock import MagicMock

import pytest

from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.auditoria_factory import crear_registro_auditoria_mock
from tests.factories.usuario_factory import crear_usuario_mock, crear_rol_mock, crear_permiso_mock


@pytest.fixture
def usuario_con_permiso():
    permiso = crear_permiso_mock(codigo="VER_AUDITORIA", descripcion="Ver auditoria")
    rol = crear_rol_mock(codigo="GERENTE_GENERAL", nombre="Gerente General", permisos=[permiso])
    return crear_usuario_mock(roles=[rol])


@pytest.fixture
def usuario_sin_permiso():
    return crear_usuario_mock()


@pytest.fixture
def mock_obtener_registros_use_case():
    uc = MagicMock()
    registros = [crear_registro_auditoria_mock()]
    uc.ejecutar_paginado.return_value = (registros, 1)
    uc.ejecutar_exportacion.return_value = registros
    return uc


@pytest.fixture
def client_auditoria(usuario_con_permiso, mock_obtener_registros_use_case):
    from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
    from app.presentacion.api.auditoria.dependencias.deps import (
        get_obtener_registros_auditoria_use_case,
    )

    def override_get_current_user():
        return usuario_con_permiso

    def override_get_obtener_registros_auditoria_use_case():
        return mock_obtener_registros_use_case

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[
        get_obtener_registros_auditoria_use_case
    ] = override_get_obtener_registros_auditoria_use_case

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestAuditoriaRouter:

    def test_obtener_registros_paginados(self, client_auditoria):
        response = client_auditoria.get("/auditoria/")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["total"] == 1
        assert data["pagina"] == 1
        assert data["tamano_pagina"] == 15
        assert data["total_paginas"] == 1
        assert data["data"][0]["categoria"] == "ACCION_NEGOCIO"
        assert data["data"][0]["evento"] == "CREAR"
        assert data["data"][0]["ip_origen"] == "200.10.20.30"

    def test_filtros_se_pasan_al_use_case(
        self, client_auditoria, mock_obtener_registros_use_case
    ):
        response = client_auditoria.get(
            "/auditoria/",
            params={
                "categoria": "AUTENTICACION",
                "evento": "LOGIN_EXITOSO",
                "rut_usuario": "12345678-9",
                "ip_origen": "200.10",
                "entidad_tipo": "prospectos",
                "fecha_desde": "2026-09-01T00:00:00",
                "fecha_hasta": "2026-09-30T23:59:59",
                "texto_busqueda": "juan",
                "pagina": 2,
                "tamano_pagina": 10,
            },
        )

        assert response.status_code == 200
        kwargs = mock_obtener_registros_use_case.ejecutar_paginado.call_args.kwargs
        assert kwargs["categoria"] == "AUTENTICACION"
        assert kwargs["evento"] == "LOGIN_EXITOSO"
        assert kwargs["rut_usuario"] == "12345678-9"
        assert kwargs["ip_origen"] == "200.10"
        assert kwargs["entidad_tipo"] == "prospectos"
        assert kwargs["texto_busqueda"] == "juan"
        assert kwargs["pagina"] == 2
        assert kwargs["tamano_pagina"] == 10

    def test_fecha_hasta_sin_hora_se_interpreta_como_fin_de_dia(
        self, client_auditoria, mock_obtener_registros_use_case
    ):
        response = client_auditoria.get("/auditoria/", params={"fecha_hasta": "2026-09-30"})

        assert response.status_code == 200
        kwargs = mock_obtener_registros_use_case.ejecutar_paginado.call_args.kwargs
        assert kwargs["fecha_hasta"].date().isoformat() == "2026-09-30"
        assert kwargs["fecha_hasta"].time() > time(23, 0)

    def test_exportar_genera_csv(self, client_auditoria):
        response = client_auditoria.get("/auditoria/exportar")

        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        lineas = response.text.strip().splitlines()
        assert lineas[0].startswith("id,fecha_registro,categoria,evento")
        assert len(lineas) == 2

    def test_requiere_permiso_ver_auditoria(self, usuario_sin_permiso):
        from app.presentacion.api.auth.dependencias.get_current_user import get_current_user

        def override_get_current_user():
            return usuario_sin_permiso

        app.dependency_overrides[get_current_user] = override_get_current_user

        from starlette.testclient import TestClient
        with TestClient(app) as c:
            response = c.get("/auditoria/")

        app.dependency_overrides.clear()

        assert response.status_code == 403
