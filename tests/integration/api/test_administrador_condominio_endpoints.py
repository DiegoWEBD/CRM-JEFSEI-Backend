import pytest
from unittest.mock import MagicMock

from app.aplicacion.administrador_condominio.servicios.consulta_administradores_service import (
    ConsultaAdministradoresService,
)
from app.aplicacion.administrador_condominio.use_cases.actualizar_administrador import (
    ActualizarAdministradorUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.obtener_administrador_por_id import (
    ObtenerAdministradorPorIdUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.obtener_administradores import (
    ObtenerAdministradoresUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.registrar_administrador import (
    RegistrarAdministradorUseCase,
)
from app.aplicacion.prospecto.servicios.consulta_prospectos_service import (
    ConsultaProspectosService,
)
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.main import app
from app.presentacion.api.administrador_condominio.deps import (
    get_actualizar_administrador_use_case,
    get_consulta_prospectos_service,
    get_obtener_administrador_por_id_use_case,
    get_obtener_administradores_use_case,
    get_registrar_administrador_use_case,
)
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from tests.factories.administrador_condominio_factory import crear_administrador_mock
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
def use_case_obtener_mock():
    mock = MagicMock(spec=ObtenerAdministradorPorIdUseCase)
    mock.ejecutar.return_value = crear_administrador_mock()
    return mock


@pytest.fixture
def use_case_lista_mock():
    mock = MagicMock(spec=ObtenerAdministradoresUseCase)
    mock.ejecutar.return_value = {'data': [], 'total': 0, 'pagina': 1, 'tamano_pagina': 25}
    return mock


@pytest.fixture
def use_case_registrar_mock():
    mock = MagicMock(spec=RegistrarAdministradorUseCase)
    mock.ejecutar.return_value = crear_administrador_mock()
    return mock


@pytest.fixture
def use_case_actualizar_mock():
    mock = MagicMock(spec=ActualizarAdministradorUseCase)
    mock.ejecutar.return_value = crear_administrador_mock()
    return mock


@pytest.fixture
def consulta_prospectos_mock():
    return MagicMock(spec=ConsultaProspectosService)


@pytest.fixture
def usuario_holder():
    return {"usuario": _usuario_con_permiso("VER_ADMINISTRADORES")}


@pytest.fixture
def client(
    usuario_holder,
    use_case_obtener_mock,
    use_case_lista_mock,
    use_case_registrar_mock,
    use_case_actualizar_mock,
    consulta_prospectos_mock,
):
    def override_get_current_user():
        return usuario_holder["usuario"]

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_administrador_por_id_use_case] = lambda: use_case_obtener_mock
    app.dependency_overrides[get_obtener_administradores_use_case] = lambda: use_case_lista_mock
    app.dependency_overrides[get_registrar_administrador_use_case] = lambda: use_case_registrar_mock
    app.dependency_overrides[get_actualizar_administrador_use_case] = lambda: use_case_actualizar_mock
    app.dependency_overrides[get_consulta_prospectos_service] = lambda: consulta_prospectos_mock

    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _payload(**kwargs):
    payload = {
        "nombre_administrador": "Administrador Test",
        "nombre_contacto": "Contacto Test",
        "telefono": "+56912345678",
        "correo": "admin@test.com",
    }
    payload.update(kwargs)
    return payload


@pytest.mark.integration
class TestAdministradorCondominioLectura:

    def test_obtener_por_id_pasa_usuario(self, client, headers_auth_validos, use_case_obtener_mock):
        response = client.get("/administradores/1", headers=headers_auth_validos)

        assert response.status_code == 200
        assert use_case_obtener_mock.ejecutar.call_args.kwargs["usuario"].rut == "11111111-1"
        assert use_case_obtener_mock.ejecutar.call_args.kwargs["id"] == 1

    def test_obtener_por_id_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_obtener_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.get("/administradores/1", headers=headers_auth_validos)

        assert response.status_code == 403
        use_case_obtener_mock.ejecutar.assert_not_called()

    def test_listar_pasa_usuario(self, client, headers_auth_validos, use_case_lista_mock):
        response = client.get("/administradores/", headers=headers_auth_validos)

        assert response.status_code == 200
        assert use_case_lista_mock.ejecutar.call_args.kwargs["usuario"].rut == "11111111-1"

    def test_listar_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_lista_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.get("/administradores/", headers=headers_auth_validos)

        assert response.status_code == 403
        use_case_lista_mock.ejecutar.assert_not_called()


@pytest.mark.integration
class TestAdministradorCondominioEscritura:

    def test_registrar_con_permiso(self, client, headers_auth_validos, use_case_registrar_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("ADMINISTRAR_ADMINISTRADORES")

        response = client.post("/administradores/", json=_payload(), headers=headers_auth_validos)

        assert response.status_code == 201
        assert use_case_registrar_mock.ejecutar.call_args.kwargs["usuario"].rut == "11111111-1"

    def test_registrar_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_registrar_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_ADMINISTRADORES")

        response = client.post("/administradores/", json=_payload(), headers=headers_auth_validos)

        assert response.status_code == 403
        use_case_registrar_mock.ejecutar.assert_not_called()

    def test_actualizar_con_permiso(self, client, headers_auth_validos, use_case_actualizar_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("ADMINISTRAR_ADMINISTRADORES")

        response = client.put("/administradores/1", json=_payload(), headers=headers_auth_validos)

        assert response.status_code == 200
        assert use_case_actualizar_mock.ejecutar.call_args.kwargs["usuario"].rut == "11111111-1"

    def test_actualizar_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_actualizar_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_ADMINISTRADORES")

        response = client.put("/administradores/1", json=_payload(), headers=headers_auth_validos)

        assert response.status_code == 403
        use_case_actualizar_mock.ejecutar.assert_not_called()

    def test_actualizar_ignora_campos_de_condominios(self, client, headers_auth_validos, use_case_actualizar_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("ADMINISTRAR_ADMINISTRADORES")

        response = client.put(
            "/administradores/1",
            json=_payload(condominios=[1, 2, 3], id_prospecto=99, id_administrador=5),
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = use_case_actualizar_mock.ejecutar.call_args.kwargs
        # Mass-assignment: los campos de condominios no llegan al caso de uso.
        assert set(kwargs.keys()) == {"usuario", "id", "nombre_administrador", "nombre_contacto", "telefono", "correo"}


@pytest.mark.integration
class TestAdministradorCondominioProspectos:

    def test_prospectos_con_obtener_todos(self, client, headers_auth_validos, use_case_obtener_mock, consulta_prospectos_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("OBTENER_PROSPECTOS_TODOS")

        response = client.get("/administradores/1/prospectos", headers=headers_auth_validos)

        assert response.status_code == 200
        consulta_prospectos_mock.obtener_por_administrador.assert_called_once_with(1)

    def test_prospectos_con_obtener_propios_scoping_por_rut(self, client, headers_auth_validos, use_case_obtener_mock, consulta_prospectos_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("OBTENER_PROSPECTOS_PROPIOS")

        response = client.get("/administradores/1/prospectos", headers=headers_auth_validos)

        assert response.status_code == 200
        consulta_prospectos_mock.obtener_por_administrador.assert_called_once_with(1, "11111111-1")

    def test_prospectos_sin_permisos_retorna_403(self, client, headers_auth_validos, use_case_obtener_mock, consulta_prospectos_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.get("/administradores/1/prospectos", headers=headers_auth_validos)

        assert response.status_code == 403
        consulta_prospectos_mock.obtener_por_administrador.assert_not_called()
