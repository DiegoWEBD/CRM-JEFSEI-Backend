import pytest
from unittest.mock import MagicMock

from app.aplicacion.archivo.use_cases.eliminar_archivo import EliminarArchivoUseCase
from app.aplicacion.archivo.use_cases.obtener_archivo_por_id import ObtenerArchivoPorIdUseCase
from app.aplicacion.archivo.use_cases.obtener_archivos_prospecto import ObtenerArchivosProspectoUseCase
from app.aplicacion.archivo.use_cases.subir_archivo import SubirArchivoUseCase
from app.dominio.usuario.usuario import Usuario
from app.main import app
from app.presentacion.api.archivo.deps import (
    get_eliminar_archivo_use_case,
    get_obtener_archivo_por_id_use_case,
    get_obtener_archivos_prospecto_use_case,
    get_subir_archivo_use_case,
)
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from tests.factories.archivo_factory import crear_archivo_mock
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
def use_case_subir_mock():
    mock = MagicMock(spec=SubirArchivoUseCase)
    mock.ejecutar.return_value = crear_archivo_mock()
    return mock


@pytest.fixture
def use_case_listar_mock():
    mock = MagicMock(spec=ObtenerArchivosProspectoUseCase)
    mock.ejecutar.return_value = [crear_archivo_mock()]
    return mock


@pytest.fixture
def use_case_descargar_mock():
    mock = MagicMock(spec=ObtenerArchivoPorIdUseCase)
    mock.ejecutar.return_value = crear_archivo_mock()
    return mock


@pytest.fixture
def use_case_eliminar_mock():
    return MagicMock(spec=EliminarArchivoUseCase)


@pytest.fixture
def usuario_holder():
    return {"usuario": _usuario_con_permiso("VER_ARCHIVOS_PROPIOS")}


@pytest.fixture
def client(
    usuario_holder,
    use_case_subir_mock,
    use_case_listar_mock,
    use_case_descargar_mock,
    use_case_eliminar_mock,
):
    def override_get_current_user():
        return usuario_holder["usuario"]

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_subir_archivo_use_case] = lambda: use_case_subir_mock
    app.dependency_overrides[get_obtener_archivos_prospecto_use_case] = lambda: use_case_listar_mock
    app.dependency_overrides[get_obtener_archivo_por_id_use_case] = lambda: use_case_descargar_mock
    app.dependency_overrides[get_eliminar_archivo_use_case] = lambda: use_case_eliminar_mock

    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _archivo_upload(nombre="documento.pdf", content_type="application/pdf"):
    return {"archivo": (nombre, b"contenido de prueba", content_type)}


@pytest.mark.integration
class TestArchivoSubir:

    def test_subir_con_permiso_administrar_pasa_usuario(self, client, headers_auth_validos, use_case_subir_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("ADMINISTRAR_ARCHIVOS_PROPIOS")

        response = client.post(
            "/prospectos/7/archivos/",
            files=_archivo_upload(),
            headers=headers_auth_validos,
        )

        assert response.status_code == 201
        kwargs = use_case_subir_mock.ejecutar.call_args.kwargs
        assert kwargs["usuario"].rut == "11111111-1"
        assert "rut_usuario" not in kwargs

    def test_subir_con_solo_permiso_ver_retorna_403(self, client, headers_auth_validos, use_case_subir_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_ARCHIVOS_PROPIOS")

        response = client.post(
            "/prospectos/7/archivos/",
            files=_archivo_upload(),
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_subir_mock.ejecutar.assert_not_called()

    def test_subir_tipo_no_permitido_retorna_400(self, client, headers_auth_validos, use_case_subir_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("ADMINISTRAR_ARCHIVOS_PROPIOS")

        response = client.post(
            "/prospectos/7/archivos/",
            files=_archivo_upload(content_type="application/x-sh"),
            headers=headers_auth_validos,
        )

        assert response.status_code == 400
        use_case_subir_mock.ejecutar.assert_not_called()


@pytest.mark.integration
class TestArchivoLectura:

    def test_listar_con_permiso_ver(self, client, headers_auth_validos, use_case_listar_mock):
        response = client.get(
            "/prospectos/7/archivos/",
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = use_case_listar_mock.ejecutar.call_args.kwargs
        assert kwargs["usuario"].rut == "11111111-1"
        assert kwargs["id_prospecto"] == 7

    def test_listar_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_listar_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.get(
            "/prospectos/7/archivos/",
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_listar_mock.ejecutar.assert_not_called()

    def test_descargar_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_descargar_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.get(
            "/prospectos/7/archivos/1",
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_descargar_mock.ejecutar.assert_not_called()

    def test_descargar_pasa_usuario(self, client, headers_auth_validos, use_case_descargar_mock):
        response = client.get(
            "/prospectos/7/archivos/1",
            headers=headers_auth_validos,
        )

        # El use case mockeado devuelve el archivo; el router responde 404 porque
        # el archivo físico no existe en disco durante el test.
        assert response.status_code == 404
        kwargs = use_case_descargar_mock.ejecutar.call_args.kwargs
        assert kwargs["usuario"].rut == "11111111-1"
        assert kwargs["id_archivo"] == 1


@pytest.mark.integration
class TestArchivoEliminar:

    def test_eliminar_con_permiso_administrar_pasa_usuario(self, client, headers_auth_validos, use_case_eliminar_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("ADMINISTRAR_ARCHIVOS_PROPIOS")

        response = client.delete(
            "/prospectos/7/archivos/1",
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = use_case_eliminar_mock.ejecutar.call_args.kwargs
        assert kwargs["usuario"].rut == "11111111-1"
        assert kwargs["id_archivo"] == 1

    def test_eliminar_con_solo_permiso_ver_retorna_403(self, client, headers_auth_validos, use_case_eliminar_mock, usuario_holder):
        usuario_holder["usuario"] = _usuario_con_permiso("VER_ARCHIVOS_PROPIOS")

        response = client.delete(
            "/prospectos/7/archivos/1",
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_eliminar_mock.ejecutar.assert_not_called()

    def test_eliminar_sin_permiso_retorna_403(self, client, headers_auth_validos, use_case_eliminar_mock, usuario_holder):
        usuario_holder["usuario"] = crear_usuario_mock()

        response = client.delete(
            "/prospectos/7/archivos/1",
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_eliminar_mock.ejecutar.assert_not_called()
