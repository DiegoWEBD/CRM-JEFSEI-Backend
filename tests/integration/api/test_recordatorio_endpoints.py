import pytest
from unittest.mock import MagicMock

from app.main import app
from app.dominio.usuario.usuario import Usuario
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.recordatorio.dependencias.deps import (
    get_obtener_recordatorios_usuario_use_case,
    get_registrar_recordatorio_use_case,
)
from app.aplicacion.recordatorio.use_cases.obtener_recordatorios import ObtenerRecordatoriosUsuarioUseCase
from app.aplicacion.recordatorio.use_cases.registrar_recordatorio import RegistrarRecordatorioUseCase
from tests.factories.usuario_factory import (
    crear_usuario_admin_mock,
    crear_usuario_mock,
    crear_rol_mock,
    crear_permiso_mock,
)
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


def _usuario_con_permiso(codigo_permiso: str) -> Usuario:
    return crear_usuario_mock(
        rut="11111111-1",
        roles=[crear_rol_mock(permisos=[crear_permiso_mock(codigo=codigo_permiso)])],
    )


@pytest.fixture
def use_case_registrar_mock():
    return MagicMock(spec=RegistrarRecordatorioUseCase)


@pytest.fixture
def usuario_holder():
    return {"usuario": _usuario_con_permiso("CREAR_RECORDATORIO_PROPIO")}


@pytest.fixture
def client_registrar(usuario_holder, use_case_registrar_mock):
    def override_get_current_user():
        return usuario_holder["usuario"]

    def override_get_registrar_recordatorio_use_case():
        return use_case_registrar_mock

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_registrar_recordatorio_use_case] = (
        override_get_registrar_recordatorio_use_case
    )

    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _payload_registrar(**kwargs):
    payload = {
        "titulo": "Llamar al cliente",
        "detalle": None,
        "prioridad": "MEDIA",
        "tipo_gestion": "LLAMADA",
        "fecha_recordatorio": "2026-12-01T10:00:00",
        "id_prospecto": None,
        "rut_usuario_destino": None,
    }
    payload.update(kwargs)
    return payload


@pytest.mark.integration
class TestRecordatorioEndpointsRegistrar:

    def test_registrar_recordatorio_creado(self, client_registrar, headers_auth_validos, use_case_registrar_mock):
        response = client_registrar.post(
            "/recordatorios/",
            json=_payload_registrar(),
            headers=headers_auth_validos,
        )

        assert response.status_code == 201
        assert response.json() == {"message": "Recordatorio creado correctamente"}
        assert use_case_registrar_mock.ejecutar.call_args.kwargs["rut_usuario"] == "11111111-1"
        assert use_case_registrar_mock.ejecutar.call_args.kwargs["rut_usuario_destino"] is None

    def test_registrar_recordatorio_con_destino(self, client_registrar, headers_auth_validos, use_case_registrar_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("CREAR_RECORDATORIO_GLOBAL")

        response = client_registrar.post(
            "/recordatorios/",
            json=_payload_registrar(rut_usuario_destino="22222222-2"),
            headers=headers_auth_validos,
        )

        assert response.status_code == 201
        assert use_case_registrar_mock.ejecutar.call_args.kwargs["rut_usuario"] == "11111111-1"
        assert use_case_registrar_mock.ejecutar.call_args.kwargs["rut_usuario_destino"] == "22222222-2"

    def test_registrar_recordatorio_sin_permisos_retorna_403(self, client_registrar, headers_auth_validos, use_case_registrar_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client_registrar.post(
            "/recordatorios/",
            json=_payload_registrar(),
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_registrar_mock.ejecutar.assert_not_called()

    def test_registrar_recordatorio_destino_sin_permiso_global_retorna_403(self, client_registrar, headers_auth_validos, use_case_registrar_mock):
        use_case_registrar_mock.ejecutar.side_effect = UsuarioNoAutorizadoException()

        response = client_registrar.post(
            "/recordatorios/",
            json=_payload_registrar(rut_usuario_destino="22222222-2"),
            headers=headers_auth_validos,
        )

        assert response.status_code == 403

    def test_registrar_recordatorio_destino_inexistente_retorna_404(self, client_registrar, headers_auth_validos, use_case_registrar_mock):
        use_case_registrar_mock.ejecutar.side_effect = RecursoNoEncontradoException(
            "El usuario con RUT 22222222-2 no existe"
        )

        response = client_registrar.post(
            "/recordatorios/",
            json=_payload_registrar(rut_usuario_destino="22222222-2"),
            headers=headers_auth_validos,
        )

        assert response.status_code == 404

    def test_registrar_recordatorio_pasa_todos_los_datos(self, client_registrar, headers_auth_validos, use_case_registrar_mock):
        response = client_registrar.post(
            "/recordatorios/",
            json=_payload_registrar(
                titulo="Cobrar cuota",
                detalle="Cuota de octubre",
                prioridad="ALTA",
                tipo_gestion="COBRANZA",
                fecha_recordatorio="2026-12-05T09:00:00",
                id_prospecto=7,
            ),
            headers=headers_auth_validos,
        )

        assert response.status_code == 201
        use_case_registrar_mock.ejecutar.assert_called_once_with(
            rut_usuario="11111111-1",
            rut_usuario_destino=None,
            titulo="Cobrar cuota",
            detalle="Cuota de octubre",
            prioridad="ALTA",
            tipo_gestion="COBRANZA",
            fecha_recordatorio="2026-12-05T09:00:00",
            id_prospecto=7,
        )
