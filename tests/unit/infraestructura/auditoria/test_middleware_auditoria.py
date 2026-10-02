from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.core.config import settings
from app.dominio.auditoria.eventos_auditoria import (
    EventoAuditoria,
    ResultadoAuditoria,
)
from app.infraestructura.auditoria.descripciones.resolvedor_nombres import (
    DatosOportunidad,
    ResolvedorNombres,
)
from app.infraestructura.auditoria.middleware_auditoria import (
    MiddlewareAuditoria,
    clasificar_evento,
    extraer_error_response,
    parsear_entidad,
)


async def endpoint_con_usuario(request: Request):
    # FastAPI siempre consume el body de las peticiones con DTO; el middleware
    # lo observa al pasar para construir la descripción.
    await request.body()
    request.state.usuario = SimpleNamespace(rut="12345678-9", nombre="Juan Perez")
    return JSONResponse({"ok": True}, status_code=201)


async def endpoint_sin_usuario(request: Request):
    return JSONResponse({"ok": True})


async def endpoint_con_error(request: Request):
    raise RuntimeError("falla interna")


async def endpoint_con_error_json(request: Request):
    return JSONResponse(
        {"detail": "Ya existe un prospecto con ese nombre"},
        status_code=409,
    )


async def endpoint_con_error_validacion(request: Request):
    return JSONResponse(
        {
            "detail": [
                {"loc": ["body", "rut"], "msg": "field required", "type": "value_error"},
                {"loc": ["body", "nombre"], "msg": "ensure this value has at least 3 characters", "type": "value_error"},
            ]
        },
        status_code=422,
    )


async def endpoint_redireccion_slash(request: Request):
    # Replica el redirect_slashes de FastAPI: /recurso -> /recurso/
    return RedirectResponse(url="/recurso/", status_code=307)


def _crear_middleware() -> MiddlewareAuditoria:
    app_interna = Starlette(routes=[
        Route("/prospectos", endpoint_con_usuario, methods=["POST"]),
        Route("/prospectos", endpoint_sin_usuario, methods=["GET"]),
        Route("/prospectos/{id}", endpoint_con_usuario, methods=["PUT", "DELETE"]),
        Route("/prospectos/{id}/asignar-ej-comercial", endpoint_con_usuario, methods=["POST"]),
        Route("/auth/login", endpoint_sin_usuario, methods=["POST"]),
        Route("/con-error", endpoint_con_error, methods=["POST"]),
        Route("/con-error-json", endpoint_con_error_json, methods=["POST"]),
        Route("/con-error-validacion", endpoint_con_error_validacion, methods=["POST"]),
        Route("/recurso", endpoint_redireccion_slash, methods=["POST"]),
        Route("/recurso/", endpoint_con_usuario, methods=["POST"]),
        Route("/procesos-comerciales/reportes", endpoint_sin_usuario, methods=["POST"]),
        Route("/procesos-comerciales/{id}/polizas", endpoint_con_usuario, methods=["POST"]),
    ])
    return MiddlewareAuditoria(app_interna)


def _mock_resolvedor() -> MagicMock:
    resolvedor = MagicMock(spec=ResolvedorNombres)
    resolvedor.nombre_prospecto.return_value = 'Torre Las Condes'
    resolvedor.nombre_usuario.return_value = 'María López'
    resolvedor.datos_oportunidad.return_value = DatosOportunidad(
        producto='Seguro Hogar',
        cliente='Jorge Maldonado Mena',
        id_prospecto=680,
    )
    return resolvedor


@pytest.fixture
def cliente_con_auditoria(monkeypatch):
    monkeypatch.setattr(settings, "CRM_AUDITORIA_HABILITADA", True)
    middleware = _crear_middleware()
    servicio = MagicMock()
    middleware.servicio_auditoria = servicio
    middleware.resolvedor_nombres = _mock_resolvedor()
    client = TestClient(middleware, raise_server_exceptions=False)
    yield client, servicio


@pytest.mark.unit
class TestClasificacionEventos:

    def test_put_es_actualizar(self):
        assert clasificar_evento("PUT", "/prospectos/5") == EventoAuditoria.ACTUALIZAR

    def test_patch_es_actualizar(self):
        assert clasificar_evento("PATCH", "/prospectos/5") == EventoAuditoria.ACTUALIZAR

    def test_delete_es_eliminar(self):
        assert clasificar_evento("DELETE", "/prospectos/5") == EventoAuditoria.ELIMINAR

    def test_post_en_coleccion_es_crear(self):
        assert clasificar_evento("POST", "/prospectos/") == EventoAuditoria.CREAR

    def test_post_en_sub_ruta_es_ejecutar_accion(self):
        evento = clasificar_evento("POST", "/prospectos/5/asignar-ej-comercial")
        assert evento == EventoAuditoria.EJECUTAR_ACCION

    def test_parsear_entidad_con_id(self):
        assert parsear_entidad("/prospectos/5/contactos") == ("prospectos", "5")

    def test_parsear_entidad_sin_id(self):
        assert parsear_entidad("/prospectos/") == ("prospectos", None)

    def test_parsear_entidad_ruta_vacia(self):
        assert parsear_entidad("/") == (None, None)


@pytest.mark.unit
class TestMiddlewareAuditoria:

    def test_post_registra_accion_de_negocio(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.post("/prospectos")

        assert response.status_code == 201
        servicio.registrar_accion_negocio.assert_called_once()
        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["evento"] == EventoAuditoria.CREAR
        assert kwargs["resultado"] == ResultadoAuditoria.EXITO
        assert kwargs["estado_http"] == 201
        assert kwargs["rut_usuario"] == "12345678-9"
        assert kwargs["nombre_usuario"] == "Juan Perez"
        assert kwargs["metodo"] == "POST"
        assert kwargs["entidad_tipo"] == "prospectos"

    def test_get_no_se_audita(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.get("/prospectos")

        assert response.status_code == 200
        servicio.registrar_accion_negocio.assert_not_called()

    def test_rutas_de_autenticacion_no_se_auditan(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.post("/auth/login")

        assert response.status_code == 200
        servicio.registrar_accion_negocio.assert_not_called()

    def test_delete_registra_eliminar(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.delete("/prospectos/5")

        assert response.status_code == 201
        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["evento"] == EventoAuditoria.ELIMINAR
        assert kwargs["entidad_tipo"] == "prospectos"
        assert kwargs["entidad_id"] == "5"

    def test_post_en_sub_ruta_registra_ejecutar_accion(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        client.post("/prospectos/5/asignar-ej-comercial")

        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["evento"] == EventoAuditoria.EJECUTAR_ACCION
        assert kwargs["entidad_id"] == "5"

    def test_x_request_id_entrante_se_propaga(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.post("/prospectos", headers={"X-Request-ID": "abc-123"})

        assert response.headers["X-Request-ID"] == "abc-123"
        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["contexto"].id_peticion == "abc-123"

    def test_x_request_id_se_genera_si_no_entrante(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.post("/prospectos")

        id_peticion = response.headers["X-Request-ID"]
        assert id_peticion
        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["contexto"].id_peticion == id_peticion

    def test_respuesta_500_se_registra_como_fallido(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.post("/con-error")

        assert response.status_code == 500
        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["resultado"] == ResultadoAuditoria.FALLIDO
        assert kwargs["estado_http"] == 500

    def test_redireccion_307_no_se_audita(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.post("/recurso", follow_redirects=False)

        assert response.status_code == 307
        servicio.registrar_accion_negocio.assert_not_called()

    def test_cadena_307_mas_201_audita_una_sola_vez(self, cliente_con_auditoria):
        # Regresión del bug: POST sin slash final generaba un registro 307 sin
        # usuario (redirect_slashes) además del registro real 201.
        client, servicio = cliente_con_auditoria

        response = client.post("/recurso")

        assert response.status_code == 201
        servicio.registrar_accion_negocio.assert_called_once()
        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["estado_http"] == 201
        assert kwargs["resultado"] == ResultadoAuditoria.EXITO
        assert kwargs["rut_usuario"] == "12345678-9"
        assert kwargs["ruta"] == "/recurso/"

    def test_fallo_de_auditoria_no_rompe_la_respuesta(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria
        servicio.registrar_accion_negocio.side_effect = RuntimeError("db caida")

        response = client.post("/prospectos")

        assert response.status_code == 201

    def test_auditoria_deshabilitada_no_registra(self, monkeypatch):
        monkeypatch.setattr(settings, "CRM_AUDITORIA_HABILITADA", False)
        middleware = _crear_middleware()
        servicio = MagicMock()
        middleware.servicio_auditoria = servicio
        client = TestClient(middleware)

        response = client.post("/prospectos")

        assert response.status_code == 201
        servicio.registrar_accion_negocio.assert_not_called()

    def test_registra_user_agent_e_ip(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        client.post("/prospectos", headers={"User-Agent": "AgenteDePrueba/1.0"})

        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        contexto = kwargs["contexto"]
        assert contexto.user_agent == "AgenteDePrueba/1.0"
        assert contexto.ip_origen


@pytest.mark.unit
class TestDescripcionEnMiddleware:

    def test_descripcion_se_construye_desde_el_body(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        client.post("/prospectos", json={"nombre_riesgo": "Torre Las Condes"})

        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["detalle"] == (
            "El usuario 12345678-9 ha registrado el prospecto Torre Las Condes"
        )

    def test_descripcion_generica_sin_plantilla(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        client.post("/recurso/")

        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["detalle"] == (
            "El usuario 12345678-9 ha creado un registro en recurso"
        )

    def test_body_no_json_se_ignora(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        client.post(
            "/prospectos",
            content=b"nombre_riesgo=Torre",
            headers={"Content-Type": "text/plain"},
        )

        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["detalle"] == "El usuario 12345678-9 ha registrado un nuevo prospecto"

    def test_reportes_no_se_audita(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.post("/procesos-comerciales/reportes", json={"filtro": 1})

        assert response.status_code == 200
        servicio.registrar_accion_negocio.assert_not_called()

    def test_descripcion_enriquecida_para_asignacion(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        client.post(
            "/prospectos/5/asignar-ej-comercial",
            json={"rut_ej_comercial": "12356487-1"},
        )

        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["detalle"] == (
            "El usuario 12345678-9 ha asignado la gestión comercial del prospecto "
            "Torre Las Condes (5) al usuario María López (12356487-1)"
        )

    def test_crear_poliza_en_sub_ruta_es_evento_crear(self, cliente_con_auditoria):
        # Regresión: crear una póliza vía POST /procesos-comerciales/{id}/polizas
        # debe registrarse como CREAR, no como acción genérica.
        client, servicio = cliente_con_auditoria

        client.post(
            "/procesos-comerciales/442/polizas",
            json={"numero_poliza": "H-002"},
        )

        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["evento"] == EventoAuditoria.CREAR
        assert kwargs["detalle"] == (
            "El usuario 12345678-9 ha registrado la póliza H-002 en la oportunidad "
            "'Seguro Hogar' (442) de Jorge Maldonado Mena (680)"
        )


@pytest.mark.unit
class TestDetalleSegunResultado:

    def test_exito_mantiene_descripcion_sin_error(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        client.post("/prospectos", json={"nombre_riesgo": "Torre Las Condes"})

        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["resultado"] == ResultadoAuditoria.EXITO
        assert "Error" not in kwargs["detalle"]

    def test_fallo_json_incluye_error_en_detalle(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.post("/con-error-json")

        assert response.status_code == 409
        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["resultado"] == ResultadoAuditoria.FALLIDO
        assert "— Error: Ya existe un prospecto con ese nombre" in kwargs["detalle"]

    def test_fallo_validacion_incluye_errores_resumidos(self, cliente_con_auditoria):
        client, servicio = cliente_con_auditoria

        response = client.post("/con-error-validacion")

        assert response.status_code == 422
        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["resultado"] == ResultadoAuditoria.FALLIDO
        assert "— Error:" in kwargs["detalle"]
        assert "body → rut: field required" in kwargs["detalle"]

    def test_fallo_sin_body_json_no_incluye_error(self, cliente_con_auditoria):
        # El endpoint de error genérico (RuntimeError) devuelve plain text,
        # así que no se extrae detail.
        client, servicio = cliente_con_auditoria

        response = client.post("/con-error")

        assert response.status_code == 500
        kwargs = servicio.registrar_accion_negocio.call_args.kwargs
        assert kwargs["resultado"] == ResultadoAuditoria.FALLIDO
        assert "Error" not in kwargs["detalle"]


@pytest.mark.unit
class TestExtraerErrorResponse:

    def test_extrae_detail_string(self):
        body = b'{"detail": "Recurso no encontrado"}'
        assert extraer_error_response(body, False) == "Recurso no encontrado"

    def test_extrae_detail_lista_validacion(self):
        body = b'{"detail": [{"loc": ["body", "email"], "msg": "invalid email", "type": "value_error"}]}'
        resultado = extraer_error_response(body, False)
        assert "body" in resultado
        assert "email" in resultado
        assert "invalid email" in resultado

    def test_retorna_none_si_truncado(self):
        assert extraer_error_response(b'{"detail": "x"}', True) is None

    def test_retorna_none_si_vacio(self):
        assert extraer_error_response(b'', False) is None

    def test_retorna_none_si_no_es_json(self):
        assert extraer_error_response(b'not json', False) is None

    def test_retorna_none_si_no_tiene_detail(self):
        assert extraer_error_response(b'{"error": "otro"}', False) is None

    def test_retorna_none_si_es_lista_raiz(self):
        assert extraer_error_response(b'[1, 2, 3]', False) is None
