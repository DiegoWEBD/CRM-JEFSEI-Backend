import pytest
from unittest.mock import MagicMock

from app.main import app
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.notificacion.dependencias.deps import (
    get_obtener_notificaciones_use_case,
    get_obtener_contador_no_leidas_use_case,
    get_marcar_notificacion_leida_use_case,
    get_marcar_notificaciones_leidas_use_case,
    get_obtener_oportunidades_en_riesgo_use_case,
)
from app.aplicacion.notificacion.use_cases.obtener_notificaciones import ObtenerNotificacionesUseCase
from app.aplicacion.notificacion.use_cases.obtener_contador_no_leidas import ObtenerContadorNoLeidasUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificacion_leida import MarcarNotificacionLeidaUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificaciones_leidas import MarcarNotificacionesLeidasUseCase
from app.aplicacion.notificacion.use_cases.obtener_oportunidades_en_riesgo import ObtenerOportunidadesEnRiesgoUseCase
from tests.factories.usuario_factory import crear_usuario_admin_mock, crear_usuario_mock, crear_rol_mock, crear_permiso_mock
from tests.factories.auth_factory import crear_token_mock, headers_auth
from tests.factories.notificacion_factory import crear_notificacion_mock


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

    def override_obtener_notificaciones():
        uc = MagicMock(spec=ObtenerNotificacionesUseCase)
        uc.ejecutar_paginado.return_value = (
            [crear_notificacion_mock(id=1), crear_notificacion_mock(id=2)],
            2,
        )
        return uc

    def override_contador():
        uc = MagicMock(spec=ObtenerContadorNoLeidasUseCase)
        uc.ejecutar.return_value = 3
        return uc

    def override_marcar_leida():
        return MagicMock(spec=MarcarNotificacionLeidaUseCase)

    def override_marcar_todas():
        uc = MagicMock(spec=MarcarNotificacionesLeidasUseCase)
        uc.ejecutar.return_value = 3
        return uc

    def override_en_riesgo():
        uc = MagicMock(spec=ObtenerOportunidadesEnRiesgoUseCase)
        uc.ejecutar_paginado.return_value = (["reporte-1"], 1)
        return uc

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_notificaciones_use_case] = override_obtener_notificaciones
    app.dependency_overrides[get_obtener_contador_no_leidas_use_case] = override_contador
    app.dependency_overrides[get_marcar_notificacion_leida_use_case] = override_marcar_leida
    app.dependency_overrides[get_marcar_notificaciones_leidas_use_case] = override_marcar_todas
    app.dependency_overrides[get_obtener_oportunidades_en_riesgo_use_case] = override_en_riesgo

    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestNotificacionesEndpoints:

    def test_obtener_notificaciones_estructura_paginada(self, client, headers_auth_validos):
        response = client.get("/notificaciones/", headers=headers_auth_validos)

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

    def test_obtener_notificaciones_pagina_2(self, client, headers_auth_validos):
        response = client.get(
            "/notificaciones/", params={"pagina": 2}, headers=headers_auth_validos
        )

        data = response.json()
        assert data["pagina"] == 2

    def test_obtener_notificaciones_tamano_personalizado(self, client, headers_auth_validos):
        response = client.get(
            "/notificaciones/", params={"tamano_pagina": 5}, headers=headers_auth_validos
        )

        data = response.json()
        assert data["tamano_pagina"] == 5

    def test_obtener_notificaciones_total_paginas(self, client, headers_auth_validos):
        from app.presentacion.api.notificacion.dependencias.deps import (
            get_obtener_notificaciones_use_case,
        )

        def override_con_30():
            uc = MagicMock(spec=ObtenerNotificacionesUseCase)
            uc.ejecutar_paginado.return_value = (
                [crear_notificacion_mock(id=i) for i in range(1, 16)],
                30,
            )
            return uc

        app.dependency_overrides[get_obtener_notificaciones_use_case] = override_con_30

        response = client.get("/notificaciones/", headers=headers_auth_validos)

        data = response.json()
        assert data["total"] == 30
        assert data["total_paginas"] == 2

    def test_obtener_notificaciones_con_filtros(self, client, headers_auth_validos):
        response = client.get(
            "/notificaciones/",
            params={"no_leidas": "true", "nivel": "CRITICO", "codigo_tipo": "SLA_VENCIDO"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    def test_nivel_invalido_retorna_400(self, client, headers_auth_validos):
        response = client.get(
            "/notificaciones/", params={"nivel": "INVALIDO"}, headers=headers_auth_validos
        )

        assert response.status_code == 400

    def test_contador_no_leidas(self, client, headers_auth_validos):
        response = client.get("/notificaciones/contador", headers=headers_auth_validos)

        assert response.status_code == 200
        assert response.json() == {"contador": 3}

    def test_marcar_leida(self, client, headers_auth_validos):
        response = client.patch(
            "/notificaciones/1/leer", headers=headers_auth_validos
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Notificación marcada como leída"}

    def test_marcar_leida_notificacion_ajena_404(self, client, headers_auth_validos):
        from app.presentacion.api.notificacion.dependencias.deps import (
            get_marcar_notificacion_leida_use_case,
        )

        def override_no_encontrada():
            uc = MagicMock(spec=MarcarNotificacionLeidaUseCase)
            uc.ejecutar.side_effect = RecursoNoEncontradoException("Notificación no encontrada")
            return uc

        app.dependency_overrides[get_marcar_notificacion_leida_use_case] = override_no_encontrada

        response = client.patch("/notificaciones/999/leer", headers=headers_auth_validos)

        assert response.status_code == 404

    def test_marcar_todas_leidas(self, client, headers_auth_validos):
        response = client.post(
            "/notificaciones/leer-todas", headers=headers_auth_validos
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Notificaciones marcadas como leídas", "total": 3}

    def test_oportunidades_en_riesgo_estructura_paginada(self, client, headers_auth_validos):
        response = client.get(
            "/notificaciones/oportunidades/en-riesgo", headers=headers_auth_validos
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "pagina" in data
        assert "tamano_pagina" in data
        assert "total_paginas" in data
        assert data["total"] == 1

    @pytest.mark.parametrize("metodo,ruta", [
        ("get", "/notificaciones/"),
        ("get", "/notificaciones/contador"),
        ("patch", "/notificaciones/1/leer"),
        ("post", "/notificaciones/leer-todas"),
        ("get", "/notificaciones/oportunidades/en-riesgo"),
    ])
    def test_sin_permiso_ver_alertas_retorna_403(self, headers_auth_validos, metodo, ruta):
        rol_sin_permiso = crear_rol_mock(
            codigo="EJECUTIVO_COMERCIAL",
            nombre="Ejecutivo Comercial",
            permisos=[crear_permiso_mock(codigo="OTRO_PERMISO", descripcion="Otro")],
        )
        usuario_sin_permiso = crear_usuario_mock(roles=[rol_sin_permiso])

        app.dependency_overrides[get_current_user] = lambda: usuario_sin_permiso

        from starlette.testclient import TestClient
        with TestClient(app) as c:
            response = getattr(c, metodo)(ruta, headers=headers_auth_validos)

        app.dependency_overrides.clear()

        assert response.status_code == 403
