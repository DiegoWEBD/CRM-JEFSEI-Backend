from unittest.mock import MagicMock

import pytest
from app.main import app
from app.aplicacion.company_seguros.use_cases.obtener_companies_paginadas import (
    ObtenerCompaniesSegurosPaginadasUseCase,
)
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.company_seguros.deps import (
    get_obtener_companies_seguros_paginadas_use_case,
)
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.company_seguros_factory import crear_company_seguros_mock, crear_factor_cuotas_mock
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock


def _usuario_con_permisos(*codigos: str):
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


@pytest.fixture
def use_case_paginado_mock():
    return MagicMock(spec=ObtenerCompaniesSegurosPaginadasUseCase)


@pytest.fixture
def client_companies(usuario_autenticado, use_case_paginado_mock):
    app.dependency_overrides[get_current_user] = lambda: usuario_autenticado
    app.dependency_overrides[get_obtener_companies_seguros_paginadas_use_case] = (
        lambda: use_case_paginado_mock
    )

    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.auth
class TestObtenerCompaniesSegurosPermisos:

    def test_sin_token_retorna_401(self, use_case_paginado_mock):
        from starlette.testclient import TestClient

        with TestClient(app) as client:
            response = client.get("/companies-seguros/")

        assert response.status_code == 401
        use_case_paginado_mock.ejecutar.assert_not_called()

    def test_get_no_requiere_administrar_companies(
        self, client_companies, use_case_paginado_mock, headers_auth_validos
    ):
        """Los selects de pólizas/cotizaciones deben seguir funcionando sin el permiso."""
        usuario_sin_permiso = _usuario_con_permisos("VER_USUARIOS")
        app.dependency_overrides[get_current_user] = lambda: usuario_sin_permiso

        use_case_paginado_mock.ejecutar.return_value = ([], 0)

        response = client_companies.get("/companies-seguros/", headers=headers_auth_validos)

        assert response.status_code == 200


@pytest.mark.integration
class TestObtenerCompaniesSegurosPaginado:

    def test_formato_estandar(self, client_companies, use_case_paginado_mock, headers_auth_validos):
        companies = [
            crear_company_seguros_mock(id=1, nombre="Chilena Rev. Seguros"),
            crear_company_seguros_mock(id=2, nombre="Mapfre"),
        ]
        use_case_paginado_mock.ejecutar.return_value = (companies, 42)

        response = client_companies.get(
            "/companies-seguros/?pagina=3&tamano_pagina=10",
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        body = response.json()

        assert set(body.keys()) == {"data", "total", "pagina", "tamano_pagina", "total_paginas"}
        assert body["total"] == 42
        assert body["pagina"] == 3
        assert body["tamano_pagina"] == 10
        assert body["total_paginas"] == 5
        assert len(body["data"]) == 2

    def test_defaults_pagina_1_tamano_15(
        self, client_companies, use_case_paginado_mock, headers_auth_validos
    ):
        use_case_paginado_mock.ejecutar.return_value = ([], 0)

        response = client_companies.get("/companies-seguros/", headers=headers_auth_validos)

        assert response.status_code == 200
        body = response.json()
        assert body["pagina"] == 1
        assert body["tamano_pagina"] == 15
        assert body["total_paginas"] == 1

    def test_total_paginas_es_1_cuando_no_hay_registros(
        self, client_companies, use_case_paginado_mock, headers_auth_validos
    ):
        use_case_paginado_mock.ejecutar.return_value = ([], 0)

        response = client_companies.get("/companies-seguros/", headers=headers_auth_validos)

        assert response.json()["total_paginas"] == 1

    def test_pasa_texto_busqueda_al_use_case(
        self, client_companies, use_case_paginado_mock, headers_auth_validos
    ):
        use_case_paginado_mock.ejecutar.return_value = ([], 0)

        client_companies.get(
            "/companies-seguros/?texto_busqueda=chilena",
            headers=headers_auth_validos,
        )

        kwargs = use_case_paginado_mock.ejecutar.call_args.kwargs
        assert kwargs["texto_busqueda"] == "chilena"
        assert kwargs["pagina"] == 1
        assert kwargs["tamano_pagina"] == 15

    def test_parametros_invalidos_retornan_422(
        self, client_companies, use_case_paginado_mock, headers_auth_validos
    ):
        response = client_companies.get(
            "/companies-seguros/?pagina=0",
            headers=headers_auth_validos,
        )

        assert response.status_code == 422

    def test_tamano_pagina_mayor_a_100_retorna_422(
        self, client_companies, use_case_paginado_mock, headers_auth_validos
    ):
        response = client_companies.get(
            "/companies-seguros/?tamano_pagina=500",
            headers=headers_auth_validos,
        )

        assert response.status_code == 422

    def test_incluye_factores_cuotas_de_cada_company(
        self, client_companies, use_case_paginado_mock, headers_auth_validos
    ):
        company = crear_company_seguros_mock(
            id=1,
            nombre="Chilena Rev. Seguros",
            factores_cuotas=[
                crear_factor_cuotas_mock(numero_cuotas=3, factor=1.02),
                crear_factor_cuotas_mock(numero_cuotas=12, factor=1.085),
            ],
        )
        use_case_paginado_mock.ejecutar.return_value = ([company], 1)

        response = client_companies.get("/companies-seguros/", headers=headers_auth_validos)

        data = response.json()["data"][0]
        assert len(data["factores_cuotas"]) == 2
        assert data["factores_cuotas"][0]["numero_cuotas"] == 3
        assert data["factores_cuotas"][0]["factor"] == 1.02

    def test_company_sin_factores_retorna_lista_vacia(
        self, client_companies, use_case_paginado_mock, headers_auth_validos
    ):
        company = crear_company_seguros_mock(id=1, factores_cuotas=[])
        use_case_paginado_mock.ejecutar.return_value = ([company], 1)

        response = client_companies.get("/companies-seguros/", headers=headers_auth_validos)

        assert response.json()["data"][0]["factores_cuotas"] == []

    def test_incluye_flag_eliminado(
        self, client_companies, use_case_paginado_mock, headers_auth_validos
    ):
        company = crear_company_seguros_mock(id=1, eliminado=False)
        use_case_paginado_mock.ejecutar.return_value = ([company], 1)

        response = client_companies.get("/companies-seguros/", headers=headers_auth_validos)

        assert response.json()["data"][0]["eliminado"] is False
