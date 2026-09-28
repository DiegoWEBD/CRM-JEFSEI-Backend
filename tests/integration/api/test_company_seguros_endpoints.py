from unittest.mock import MagicMock

import pytest
from app.main import app
from app.aplicacion.company_seguros.use_cases.actualizar_factores_cuotas import ActualizarFactoresCuotasUseCase
from app.aplicacion.company_seguros.use_cases.actualizar_nombre_company import ActualizarNombreCompanyUseCase
from app.aplicacion.company_seguros.use_cases.crear_company import CrearCompanyUseCase
from app.aplicacion.company_seguros.use_cases.eliminar_company import EliminarCompanyUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.company_seguros.deps import (
    get_actualizar_factores_cuotas_use_case,
    get_actualizar_nombre_company_use_case,
    get_crear_company_use_case,
    get_eliminar_company_use_case,
)
from app.presentacion.api.exceptions.bad_request_exception import BadRequestException
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.company_seguros_factory import crear_company_seguros_mock
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock


def _usuario_con_permisos(*codigos: str):
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


@pytest.fixture
def usuario_admin_companies():
    return _usuario_con_permisos("ADMINISTRAR_COMPANIES")


@pytest.fixture
def usuario_sin_permiso_companies():
    return _usuario_con_permisos("VER_USUARIOS")


@pytest.fixture
def use_case_crear_mock():
    return MagicMock(spec=CrearCompanyUseCase)


@pytest.fixture
def use_case_actualizar_mock():
    return MagicMock(spec=ActualizarNombreCompanyUseCase)


@pytest.fixture
def use_case_eliminar_mock():
    return MagicMock(spec=EliminarCompanyUseCase)


@pytest.fixture
def use_case_factores_mock():
    return MagicMock(spec=ActualizarFactoresCuotasUseCase)


def _client(usuario, use_case_crear, use_case_actualizar, use_case_eliminar, use_case_factores):
    app.dependency_overrides[get_current_user] = lambda: usuario
    app.dependency_overrides[get_crear_company_use_case] = lambda: use_case_crear
    app.dependency_overrides[get_actualizar_nombre_company_use_case] = lambda: use_case_actualizar
    app.dependency_overrides[get_eliminar_company_use_case] = lambda: use_case_eliminar
    app.dependency_overrides[get_actualizar_factores_cuotas_use_case] = lambda: use_case_factores

    from starlette.testclient import TestClient

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def client_admin(
    usuario_admin_companies,
    use_case_crear_mock,
    use_case_actualizar_mock,
    use_case_eliminar_mock,
    use_case_factores_mock,
):
    yield from _client(
        usuario_admin_companies,
        use_case_crear_mock,
        use_case_actualizar_mock,
        use_case_eliminar_mock,
        use_case_factores_mock,
    )


@pytest.fixture
def client_sin_permiso(
    usuario_sin_permiso_companies,
    use_case_crear_mock,
    use_case_actualizar_mock,
    use_case_eliminar_mock,
    use_case_factores_mock,
):
    yield from _client(
        usuario_sin_permiso_companies,
        use_case_crear_mock,
        use_case_actualizar_mock,
        use_case_eliminar_mock,
        use_case_factores_mock,
    )


@pytest.mark.auth
class TestEndpointsCompaniesRequierenPermiso:

    def test_post_sin_permiso_retorna_403(
        self, client_sin_permiso, use_case_crear_mock, headers_auth_validos
    ):
        response = client_sin_permiso.post(
            "/companies-seguros/", json={"nombre": "Mapfre"}, headers=headers_auth_validos
        )

        assert response.status_code == 403
        use_case_crear_mock.ejecutar.assert_not_called()

    def test_put_sin_permiso_retorna_403(
        self, client_sin_permiso, use_case_actualizar_mock, headers_auth_validos
    ):
        response = client_sin_permiso.put(
            "/companies-seguros/1", json={"nombre": "Mapfre"}, headers=headers_auth_validos
        )

        assert response.status_code == 403
        use_case_actualizar_mock.ejecutar.assert_not_called()

    def test_delete_sin_permiso_retorna_403(
        self, client_sin_permiso, use_case_eliminar_mock, headers_auth_validos
    ):
        response = client_sin_permiso.delete(
            "/companies-seguros/1", headers=headers_auth_validos
        )

        assert response.status_code == 403
        use_case_eliminar_mock.ejecutar.assert_not_called()

    def test_put_factores_sin_permiso_retorna_403(
        self, client_sin_permiso, use_case_factores_mock, headers_auth_validos
    ):
        response = client_sin_permiso.put(
            "/companies-seguros/1/factores-cuotas",
            json={"factores": [{"numero_cuotas": 3, "factor": 1.02}]},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_factores_mock.ejecutar.assert_not_called()

    def test_no_autenticado_retorna_401(self, use_case_crear_mock):
        from starlette.testclient import TestClient

        app.dependency_overrides[get_crear_company_use_case] = lambda: use_case_crear_mock

        with TestClient(app) as client:
            response = client.post("/companies-seguros/", json={"nombre": "Mapfre"})

        app.dependency_overrides.clear()

        assert response.status_code == 401


@pytest.mark.integration
class TestCrearCompanyEndpoint:

    def test_con_permiso_retorna_201(self, client_admin, use_case_crear_mock, headers_auth_validos):
        use_case_crear_mock.ejecutar.return_value = crear_company_seguros_mock(id=10, nombre="Mapfre")

        response = client_admin.post(
            "/companies-seguros/", json={"nombre": "Mapfre"}, headers=headers_auth_validos
        )

        assert response.status_code == 201
        body = response.json()
        assert body["data"]["id"] == 10
        assert body["data"]["nombre"] == "Mapfre"
        use_case_crear_mock.ejecutar.assert_called_once_with(nombre="Mapfre")

    def test_nombre_duplicado_retorna_409(self, client_admin, use_case_crear_mock, headers_auth_validos):
        use_case_crear_mock.ejecutar.side_effect = RecursoYaExisteException(
            "Ya existe una compañía con ese nombre"
        )

        response = client_admin.post(
            "/companies-seguros/", json={"nombre": "Mapfre"}, headers=headers_auth_validos
        )

        assert response.status_code == 409

    def test_nombre_vacio_retorna_400(self, client_admin, use_case_crear_mock, headers_auth_validos):
        use_case_crear_mock.ejecutar.side_effect = BadRequestException(
            "El nombre de la compañía es obligatorio"
        )

        response = client_admin.post(
            "/companies-seguros/", json={"nombre": "   "}, headers=headers_auth_validos
        )

        assert response.status_code == 400

    def test_body_invalido_retorna_422(self, client_admin, headers_auth_validos):
        response = client_admin.post(
            "/companies-seguros/", json={"otro_campo": "x"}, headers=headers_auth_validos
        )

        assert response.status_code == 422


@pytest.mark.integration
class TestActualizarCompanyEndpoint:

    def test_renombra_company(self, client_admin, use_case_actualizar_mock, headers_auth_validos):
        response = client_admin.put(
            "/companies-seguros/1",
            json={"nombre": "Mapfre Chile"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        use_case_actualizar_mock.ejecutar.assert_called_once_with(id=1, nombre="Mapfre Chile")

    def test_company_inexistente_retorna_404(
        self, client_admin, use_case_actualizar_mock, headers_auth_validos
    ):
        use_case_actualizar_mock.ejecutar.side_effect = RecursoNoEncontradoException(
            "Compañía no encontrada"
        )

        response = client_admin.put(
            "/companies-seguros/999", json={"nombre": "Zurich"}, headers=headers_auth_validos
        )

        assert response.status_code == 404

    def test_nombre_duplicado_retorna_409(
        self, client_admin, use_case_actualizar_mock, headers_auth_validos
    ):
        use_case_actualizar_mock.ejecutar.side_effect = RecursoYaExisteException(
            "Ya existe una compañía con ese nombre"
        )

        response = client_admin.put(
            "/companies-seguros/1", json={"nombre": "Zurich"}, headers=headers_auth_validos
        )

        assert response.status_code == 409


@pytest.mark.integration
class TestEliminarCompanyEndpoint:

    def test_eliminar_retorna_200(self, client_admin, use_case_eliminar_mock, headers_auth_validos):
        response = client_admin.delete("/companies-seguros/1", headers=headers_auth_validos)

        assert response.status_code == 200
        use_case_eliminar_mock.ejecutar.assert_called_once_with(id=1)

    def test_company_inexistente_retorna_404(
        self, client_admin, use_case_eliminar_mock, headers_auth_validos
    ):
        use_case_eliminar_mock.ejecutar.side_effect = RecursoNoEncontradoException(
            "Compañía no encontrada"
        )

        response = client_admin.delete("/companies-seguros/999", headers=headers_auth_validos)

        assert response.status_code == 404


@pytest.mark.integration
class TestActualizarFactoresCuotasEndpoint:

    def test_reemplaza_lista_de_factores(self, client_admin, use_case_factores_mock, headers_auth_validos):
        response = client_admin.put(
            "/companies-seguros/1/factores-cuotas",
            json={"factores": [{"numero_cuotas": 3, "factor": 1.02}, {"numero_cuotas": 12, "factor": 1.085}]},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = use_case_factores_mock.ejecutar.call_args.kwargs
        assert kwargs["id_company"] == 1
        assert kwargs["factores"] == [
            {"numero_cuotas": 3, "factor": 1.02},
            {"numero_cuotas": 12, "factor": 1.085},
        ]

    def test_lista_vacia_es_valida(self, client_admin, use_case_factores_mock, headers_auth_validos):
        response = client_admin.put(
            "/companies-seguros/1/factores-cuotas",
            json={"factores": []},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        assert use_case_factores_mock.ejecutar.call_args.kwargs["factores"] == []

    def test_factores_invalidos_retornan_400(self, client_admin, use_case_factores_mock, headers_auth_validos):
        use_case_factores_mock.ejecutar.side_effect = BadRequestException("El factor debe ser mayor a 0")

        response = client_admin.put(
            "/companies-seguros/1/factores-cuotas",
            json={"factores": [{"numero_cuotas": 3, "factor": 0}]},
            headers=headers_auth_validos,
        )

        assert response.status_code == 400

    def test_company_inexistente_retorna_404(self, client_admin, use_case_factores_mock, headers_auth_validos):
        use_case_factores_mock.ejecutar.side_effect = RecursoNoEncontradoException(
            "Compañía no encontrada"
        )

        response = client_admin.put(
            "/companies-seguros/999/factores-cuotas",
            json={"factores": []},
            headers=headers_auth_validos,
        )

        assert response.status_code == 404

    def test_factor_con_muchos_decimales_no_se_trunca(
        self, client_admin, use_case_factores_mock, headers_auth_validos
    ):
        response = client_admin.put(
            "/companies-seguros/1/factores-cuotas",
            json={"factores": [{"numero_cuotas": 12, "factor": 1.0855555555}]},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = use_case_factores_mock.ejecutar.call_args.kwargs
        assert kwargs["factores"] == [
            {"numero_cuotas": 12, "factor": 1.0855555555}
        ]
