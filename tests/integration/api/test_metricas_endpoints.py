import pytest
from unittest.mock import MagicMock
from tests.integration.api.conftest_api import *

ENDPOINTS_METRICAS_DASHBOARD = [
    ('/metricas/prima-neta-mensual', {'total_prima_neta': 100.0, 'variacion_mes_anterior': 5.0, 'mes_label': 'Noviembre 2026'}),
    ('/metricas/comision-mensual', {'total_comision': 10.0, 'mes_label': 'Noviembre 2026'}),
    ('/metricas/tendencia-12-meses', [{'mes': 'Nov', 'prima_neta': 100.0}]),
    ('/metricas/prima-por-compania', [{'nombre': 'Compania', 'valor': 100.0}]),
    ('/metricas/compania-top', {'nombre': 'Compania', 'prima_neta': 100.0}),
    ('/metricas/prima-por-ejecutivo', [{'nombre': 'Ejecutivo', 'valor': 100.0}]),
    ('/metricas/prima-por-ramo', [{'nombre': 'Ramo', 'valor': 100.0}]),
    ('/metricas/actividades-por-tipo', [{'tipo': 'llamada', 'concretadas': 1, 'pendientes': 2}]),
    ('/metricas/resumen-actividades', {'agendadas': 3, 'concretadas': 1, 'pendientes': 2, 'porcentaje_cumplimiento': 33.0}),
    ('/metricas/polizas-por-comuna', [{'nombre': 'Comuna', 'cantidad': 1}]),
    ('/metricas/polizas-por-sexo', []),
    ('/metricas/polizas-por-rango-edad', []),
    ('/metricas/polizas-por-ramo', [{'nombre': 'Ramo', 'cantidad': 1}]),
]

PROVIDERS_METRICAS_DASHBOARD = {
    '/metricas/prima-neta-mensual': 'get_obtener_prima_neta_mensual_use_case',
    '/metricas/comision-mensual': 'get_obtener_comision_mensual_use_case',
    '/metricas/tendencia-12-meses': 'get_obtener_tendencia_12_meses_use_case',
    '/metricas/prima-por-compania': 'get_obtener_prima_por_compania_use_case',
    '/metricas/compania-top': 'get_obtener_compania_top_use_case',
    '/metricas/prima-por-ejecutivo': 'get_obtener_prima_por_ejecutivo_use_case',
    '/metricas/prima-por-ramo': 'get_obtener_prima_por_ramo_use_case',
    '/metricas/actividades-por-tipo': 'get_obtener_actividades_por_tipo_use_case',
    '/metricas/resumen-actividades': 'get_obtener_resumen_actividades_use_case',
    '/metricas/polizas-por-comuna': 'get_obtener_polizas_por_comuna_use_case',
    '/metricas/polizas-por-sexo': 'get_obtener_polizas_por_sexo_use_case',
    '/metricas/polizas-por-rango-edad': 'get_obtener_polizas_por_rango_edad_use_case',
    '/metricas/polizas-por-ramo': 'get_obtener_polizas_por_ramo_use_case',
}

ENDPOINTS_PROYECCIONES = [
    ('/metricas/prima-cotizada', {'prima_cotizada': 150.0}),
    ('/metricas/prima-potencial-estimada', {'prima_potencial_estimada': 120.0}),
    ('/metricas/prima-esperada', {'prima_esperada': 60.0}),
    (
        '/metricas/proyeccion-prima-esperada',
        [{'mes': '2026-01', 'prima_esperada': 30.0}],
    ),
]

PROVIDERS_PROYECCIONES = {
    '/metricas/prima-cotizada': 'get_obtener_prima_cotizada_use_case',
    '/metricas/prima-potencial-estimada': 'get_obtener_prima_potencial_estimada_use_case',
    '/metricas/prima-esperada': 'get_obtener_prima_esperada_use_case',
    '/metricas/proyeccion-prima-esperada': 'get_obtener_proyeccion_prima_esperada_use_case',
}


@pytest.mark.integration
class TestMetricasEndpoints:

    def test_kpis_comerciales(self, client, headers_auth_validos):
        from app.presentacion.api.metricas.dependencias.deps import get_obtener_kpis_comerciales_use_case

        def override_get_kpis():
            uc = MagicMock()
            uc.ejecutar.return_value = {
                "prima_neta": 50000,
                "tasa_cierre": 0.35,
                "tasa_renovacion": 0.80,
            }
            return uc

        app.dependency_overrides[get_obtener_kpis_comerciales_use_case] = override_get_kpis

        from starlette.testclient import TestClient
        with TestClient(app) as c:
            response = c.get("/metricas/kpis-comerciales", headers=headers_auth_validos)

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "ruta,respuesta_esperada",
        ENDPOINTS_METRICAS_DASHBOARD,
        ids=[ruta for ruta, _ in ENDPOINTS_METRICAS_DASHBOARD],
    )
    def test_metrica_dashboard(
        self, ruta, respuesta_esperada, client, headers_auth_validos
    ):
        from app.presentacion.api.metricas.dependencias import deps
        from starlette.testclient import TestClient

        provider = getattr(deps, PROVIDERS_METRICAS_DASHBOARD[ruta])

        def override_get_use_case():
            uc = MagicMock()
            uc.ejecutar.return_value = respuesta_esperada
            return uc

        app.dependency_overrides[provider] = override_get_use_case

        with TestClient(app) as c:
            response = c.get(ruta, headers=headers_auth_validos)

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "ruta", [ruta for ruta, _ in ENDPOINTS_METRICAS_DASHBOARD]
    )
    def test_metrica_dashboard_con_periodo(
        self, ruta, client, headers_auth_validos
    ):
        from app.presentacion.api.metricas.dependencias import deps
        from starlette.testclient import TestClient

        provider = getattr(deps, PROVIDERS_METRICAS_DASHBOARD[ruta])

        def override_get_use_case():
            uc = MagicMock()
            uc.ejecutar.return_value = {}
            return uc

        app.dependency_overrides[provider] = override_get_use_case

        with TestClient(app) as c:
            response = c.get(
                ruta,
                params={'mes': 11, 'year': 2026},
                headers=headers_auth_validos,
            )

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "ruta,respuesta_esperada",
        ENDPOINTS_PROYECCIONES,
        ids=[ruta for ruta, _ in ENDPOINTS_PROYECCIONES],
    )
    def test_proyeccion_dashboard(
        self, ruta, respuesta_esperada, client, headers_auth_validos
    ):
        from app.presentacion.api.metricas.dependencias import deps
        from starlette.testclient import TestClient

        provider = getattr(deps, PROVIDERS_PROYECCIONES[ruta])

        def override_get_use_case():
            uc = MagicMock()
            uc.ejecutar.return_value = respuesta_esperada
            return uc

        app.dependency_overrides[provider] = override_get_use_case

        with TestClient(app) as c:
            response = c.get(ruta, headers=headers_auth_validos)

        assert response.status_code == 200

    def test_metricas_sin_permiso(self, client):
        from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
        from tests.factories.usuario_factory import crear_usuario_mock, crear_rol_mock, crear_permiso_mock

        permisos_vacios = []
        rol_sin_permisos = crear_rol_mock(permisos=permisos_vacios)
        usuario_sin_permiso = crear_usuario_mock(roles=[rol_sin_permisos])

        def override_get_current_user():
            return usuario_sin_permiso

        app.dependency_overrides[get_current_user] = override_get_current_user

        from starlette.testclient import TestClient
        with TestClient(app) as c:
            response = c.get("/metricas/kpis-comerciales")

        assert response.status_code == 403

    @pytest.mark.parametrize(
        "ruta",
        [ruta for ruta, _ in ENDPOINTS_METRICAS_DASHBOARD]
        + [ruta for ruta, _ in ENDPOINTS_PROYECCIONES],
    )
    def test_metrica_dashboard_sin_permiso(self, ruta, client):
        from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
        from tests.factories.usuario_factory import crear_usuario_mock, crear_rol_mock

        rol_sin_permisos = crear_rol_mock(permisos=[])
        usuario_sin_permiso = crear_usuario_mock(roles=[rol_sin_permisos])

        def override_get_current_user():
            return usuario_sin_permiso

        app.dependency_overrides[get_current_user] = override_get_current_user

        from starlette.testclient import TestClient
        with TestClient(app) as c:
            response = c.get(ruta)

        assert response.status_code == 403
