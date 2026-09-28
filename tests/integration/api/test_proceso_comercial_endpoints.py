from datetime import datetime
from unittest.mock import MagicMock

import pytest
from app.main import app
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.proceso_comercial.dependencias.deps import get_actualizar_fecha_estimada_cierre_use_case, get_actualizar_probabilidad_cierre_ejecutivo_use_case
from app.presentacion.api.solicitud_cotizacion.dependencias.deps import get_obtener_procesos_comerciales_use_case
from app.aplicacion.proceso_comercial.use_cases.actualizar_fecha_estimada_cierre import ActualizarFechaEstimadaCierreUseCase
from app.aplicacion.proceso_comercial.use_cases.actualizar_probabilidad_cierre_ejecutivo import ActualizarProbabilidadCierreEjecutivoUseCase
from app.aplicacion.proceso_comercial.use_cases.obtener_procesos_comerciales import ObtenerProcesosComercialesUseCase
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock
from tests.factories.auth_factory import crear_token_mock, headers_auth


def _usuario_con_permisos(*codigos: str) -> Usuario:
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


@pytest.fixture
def usuario_propios():
    return _usuario_con_permisos("ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS")


@pytest.fixture
def usuario_solo_global():
    return _usuario_con_permisos("ADMINISTRAR_PROCESOS_COMERCIALES")


@pytest.fixture
def use_case_actualizar_mock():
    return MagicMock(spec=ActualizarFechaEstimadaCierreUseCase)


@pytest.fixture
def use_case_probabilidad_mock():
    return MagicMock(spec=ActualizarProbabilidadCierreEjecutivoUseCase)


@pytest.fixture
def client_propios(usuario_propios, use_case_actualizar_mock, use_case_probabilidad_mock):
    def override_get_current_user():
        return usuario_propios

    def override_use_case():
        return use_case_actualizar_mock

    def override_use_case_probabilidad():
        return use_case_probabilidad_mock

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_actualizar_fecha_estimada_cierre_use_case] = override_use_case
    app.dependency_overrides[get_actualizar_probabilidad_cierre_ejecutivo_use_case] = override_use_case_probabilidad

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_solo_global(usuario_solo_global, use_case_actualizar_mock, use_case_probabilidad_mock):
    def override_get_current_user():
        return usuario_solo_global

    def override_use_case():
        return use_case_actualizar_mock

    def override_use_case_probabilidad():
        return use_case_probabilidad_mock

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_actualizar_fecha_estimada_cierre_use_case] = override_use_case
    app.dependency_overrides[get_actualizar_probabilidad_cierre_ejecutivo_use_case] = override_use_case_probabilidad

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestActualizarFechaEstimadaCierreEndpoints:

    def test_actualizar_fecha_exitosa(self, client_propios, use_case_actualizar_mock, headers_auth_validos):
        response = client_propios.patch(
            "/procesos-comerciales/1/fecha-estimada-cierre",
            json={"fecha_estimada_cierre": "2026-10-15"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        use_case_actualizar_mock.ejecutar.assert_called_once()
        kwargs = use_case_actualizar_mock.ejecutar.call_args.kwargs
        assert kwargs["id"] == 1
        assert isinstance(kwargs["fecha_estimada_cierre"], datetime)
        assert kwargs["fecha_estimada_cierre"].year == 2026
        assert kwargs["fecha_estimada_cierre"].month == 10
        assert kwargs["fecha_estimada_cierre"].day == 15

    def test_actualizar_fecha_null_limpia_el_campo(
        self, client_propios, use_case_actualizar_mock, headers_auth_validos
    ):
        response = client_propios.patch(
            "/procesos-comerciales/1/fecha-estimada-cierre",
            json={"fecha_estimada_cierre": None},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = use_case_actualizar_mock.ejecutar.call_args.kwargs
        assert kwargs["fecha_estimada_cierre"] is None

    @pytest.mark.auth
    def test_sin_permiso_propios_retorna_403(self, client_solo_global, headers_auth_validos):
        response = client_solo_global.patch(
            "/procesos-comerciales/1/fecha-estimada-cierre",
            json={"fecha_estimada_cierre": "2026-10-15"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403

    @pytest.mark.auth
    def test_no_autenticado_retorna_401(self, use_case_actualizar_mock):
        from starlette.testclient import TestClient
        app.dependency_overrides[get_actualizar_fecha_estimada_cierre_use_case] = lambda: use_case_actualizar_mock
        try:
            with TestClient(app) as c:
                response = c.patch(
                    "/procesos-comerciales/1/fecha-estimada-cierre",
                    json={"fecha_estimada_cierre": "2026-10-15"},
                )
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.auth
    def test_no_es_el_ejecutivo_asignado_retorna_403(
        self, client_propios, use_case_actualizar_mock, headers_auth_validos
    ):
        use_case_actualizar_mock.ejecutar.side_effect = UsuarioNoAutorizadoException(
            "No autorizado"
        )

        response = client_propios.patch(
            "/procesos-comerciales/1/fecha-estimada-cierre",
            json={"fecha_estimada_cierre": "2026-10-15"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403

    def test_proceso_cerrado_retorna_409(
        self, client_propios, use_case_actualizar_mock, headers_auth_validos
    ):
        use_case_actualizar_mock.ejecutar.side_effect = ConflictoEnAccionException(
            "La oportunidad está cerrada"
        )

        response = client_propios.patch(
            "/procesos-comerciales/1/fecha-estimada-cierre",
            json={"fecha_estimada_cierre": "2026-10-15"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 409

    def test_proceso_no_encontrado_retorna_404(
        self, client_propios, use_case_actualizar_mock, headers_auth_validos
    ):
        use_case_actualizar_mock.ejecutar.side_effect = RecursoNoEncontradoException(
            "No encontrada"
        )

        response = client_propios.patch(
            "/procesos-comerciales/999/fecha-estimada-cierre",
            json={"fecha_estimada_cierre": "2026-10-15"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 404

    def test_fecha_invalida_retorna_422(self, client_propios, headers_auth_validos):
        response = client_propios.patch(
            "/procesos-comerciales/1/fecha-estimada-cierre",
            json={"fecha_estimada_cierre": "fecha-mala"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 422


@pytest.mark.integration
class TestActualizarProbabilidadCierreEjecutivoEndpoints:

    def test_actualizar_probabilidad_exitosa(
        self, client_propios, use_case_probabilidad_mock, headers_auth_validos
    ):
        response = client_propios.patch(
            "/procesos-comerciales/1/probabilidad-cierre-ejecutivo",
            json={"probabilidad_cierre_ejecutivo": 0.75},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        use_case_probabilidad_mock.ejecutar.assert_called_once()
        kwargs = use_case_probabilidad_mock.ejecutar.call_args.kwargs
        assert kwargs["id"] == 1
        assert kwargs["probabilidad_cierre_ejecutivo"] == 0.75

    def test_limpiar_probabilidad_con_null(
        self, client_propios, use_case_probabilidad_mock, headers_auth_validos
    ):
        response = client_propios.patch(
            "/procesos-comerciales/1/probabilidad-cierre-ejecutivo",
            json={"probabilidad_cierre_ejecutivo": None},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = use_case_probabilidad_mock.ejecutar.call_args.kwargs
        assert kwargs["probabilidad_cierre_ejecutivo"] is None

    @pytest.mark.auth
    def test_sin_permiso_propios_retorna_403(self, client_solo_global, headers_auth_validos):
        response = client_solo_global.patch(
            "/procesos-comerciales/1/probabilidad-cierre-ejecutivo",
            json={"probabilidad_cierre_ejecutivo": 0.75},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403

    @pytest.mark.auth
    def test_no_autenticado_retorna_401(self, use_case_probabilidad_mock):
        from starlette.testclient import TestClient
        app.dependency_overrides[get_actualizar_probabilidad_cierre_ejecutivo_use_case] = (
            lambda: use_case_probabilidad_mock
        )
        try:
            with TestClient(app) as c:
                response = c.patch(
                    "/procesos-comerciales/1/probabilidad-cierre-ejecutivo",
                    json={"probabilidad_cierre_ejecutivo": 0.75},
                )
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.auth
    def test_no_es_el_ejecutivo_asignado_retorna_403(
        self, client_propios, use_case_probabilidad_mock, headers_auth_validos
    ):
        use_case_probabilidad_mock.ejecutar.side_effect = UsuarioNoAutorizadoException(
            "No autorizado"
        )

        response = client_propios.patch(
            "/procesos-comerciales/1/probabilidad-cierre-ejecutivo",
            json={"probabilidad_cierre_ejecutivo": 0.75},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403

    def test_proceso_cerrado_retorna_409(
        self, client_propios, use_case_probabilidad_mock, headers_auth_validos
    ):
        use_case_probabilidad_mock.ejecutar.side_effect = ConflictoEnAccionException(
            "La oportunidad está cerrada"
        )

        response = client_propios.patch(
            "/procesos-comerciales/1/probabilidad-cierre-ejecutivo",
            json={"probabilidad_cierre_ejecutivo": 0.75},
            headers=headers_auth_validos,
        )

        assert response.status_code == 409

    def test_proceso_no_encontrado_retorna_404(
        self, client_propios, use_case_probabilidad_mock, headers_auth_validos
    ):
        use_case_probabilidad_mock.ejecutar.side_effect = RecursoNoEncontradoException(
            "No encontrada"
        )

        response = client_propios.patch(
            "/procesos-comerciales/999/probabilidad-cierre-ejecutivo",
            json={"probabilidad_cierre_ejecutivo": 0.75},
            headers=headers_auth_validos,
        )

        assert response.status_code == 404

    @pytest.mark.parametrize("valor", [1.5, -0.1])
    def test_probabilidad_fuera_de_rango_retorna_422(
        self, client_propios, headers_auth_validos, valor
    ):
        response = client_propios.patch(
            "/procesos-comerciales/1/probabilidad-cierre-ejecutivo",
            json={"probabilidad_cierre_ejecutivo": valor},
            headers=headers_auth_validos,
        )

        assert response.status_code == 422


@pytest.mark.integration
class TestObtenerProcesosComercialesSerializacion:

    def test_respuesta_incluye_fecha_estimada_cierre(self, headers_auth_validos):
        fecha = datetime(2026, 10, 15, 0, 0, 0)
        proceso = crear_proceso_comercial_mock(fecha_estimada_cierre=fecha)
        usuario = _usuario_con_permisos("ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS")

        def override_get_current_user():
            return usuario

        def override_obtener():
            uc = MagicMock(spec=ObtenerProcesosComercialesUseCase)
            uc.ejecutar.return_value = [proceso]
            return uc

        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_obtener_procesos_comerciales_use_case] = override_obtener

        try:
            from starlette.testclient import TestClient
            with TestClient(app) as c:
                response = c.get("/prospectos/1/procesos-comerciales", headers=headers_auth_validos)
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert "oportunidades" in data
        assert len(data["oportunidades"]) == 1
        assert data["oportunidades"][0]["fecha_estimada_cierre"] is not None

    def test_respuesta_incluye_probabilidades_de_cierre(self, headers_auth_validos):
        proceso = crear_proceso_comercial_mock(
            probabilidad_cierre_sistema=0.45,
            probabilidad_cierre_ejecutivo=0.75,
        )
        usuario = _usuario_con_permisos("ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS")

        def override_get_current_user():
            return usuario

        def override_obtener():
            uc = MagicMock(spec=ObtenerProcesosComercialesUseCase)
            uc.ejecutar.return_value = [proceso]
            return uc

        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_obtener_procesos_comerciales_use_case] = override_obtener

        try:
            from starlette.testclient import TestClient
            with TestClient(app) as c:
                response = c.get("/prospectos/1/procesos-comerciales", headers=headers_auth_validos)
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        oportunidad = response.json()["oportunidades"][0]
        assert oportunidad["probabilidad_cierre_sistema"] == 0.45
        assert oportunidad["probabilidad_cierre_ejecutivo"] == 0.75

    def test_respuesta_probabilidad_ejecutivo_null(self, headers_auth_validos):
        proceso = crear_proceso_comercial_mock(
            probabilidad_cierre_sistema=0.45,
            probabilidad_cierre_ejecutivo=None,
        )
        usuario = _usuario_con_permisos("ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS")

        def override_get_current_user():
            return usuario

        def override_obtener():
            uc = MagicMock(spec=ObtenerProcesosComercialesUseCase)
            uc.ejecutar.return_value = [proceso]
            return uc

        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_obtener_procesos_comerciales_use_case] = override_obtener

        try:
            from starlette.testclient import TestClient
            with TestClient(app) as c:
                response = c.get("/prospectos/1/procesos-comerciales", headers=headers_auth_validos)
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        oportunidad = response.json()["oportunidades"][0]
        assert oportunidad["probabilidad_cierre_sistema"] == 0.45
        assert oportunidad["probabilidad_cierre_ejecutivo"] is None
