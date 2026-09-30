import pytest
from unittest.mock import MagicMock

from starlette.websockets import WebSocketDisconnect

from app.aplicacion.notificacion.use_cases.marcar_notificacion_leida import MarcarNotificacionLeidaUseCase
from app.aplicacion.notificacion.use_cases.marcar_notificaciones_leidas import MarcarNotificacionesLeidasUseCase
from app.aplicacion.usuario.use_cases.obtener_usuario import ObtenerUsuarioUseCase
from app.core.hub_notificaciones import (
    EVENTO_CONEXION_ABIERTA,
    EVENTO_NOTIFICACIONES_ACTUALIZADAS,
    hub,
)
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from app.infraestructura.auth.jwt_authentication_service import JwtAuthenticationService
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.notificacion.dependencias.deps import (
    get_marcar_notificacion_leida_use_case,
    get_marcar_notificaciones_leidas_use_case,
)
from app.presentacion.api.usuario.deps import get_obtener_usuario_use_case
from tests.factories.auth_factory import crear_token_mock, headers_auth
from tests.factories.usuario_factory import (
    crear_permiso_mock,
    crear_rol_mock,
    crear_usuario_admin_mock,
    crear_usuario_mock,
)

RUT_ADMIN = '12345678-9'
RUT_SIN_PERMISO = '22222222-2'


def _usuario_sin_ver_alertas() -> object:
    rol = crear_rol_mock(
        codigo='EJECUTIVO_COMERCIAL',
        nombre='Ejecutivo Comercial',
        permisos=[crear_permiso_mock(codigo='OTRO_PERMISO', descripcion='Otro')],
    )
    return crear_usuario_mock(rut=RUT_SIN_PERMISO, roles=[rol])


def _ticket(rut: str = RUT_ADMIN) -> str:
    return JwtAuthenticationService().crear_ticket_websocket(rut)


@pytest.fixture
def usuario_autenticado():
    return crear_usuario_admin_mock()


@pytest.fixture
def headers_auth_validos():
    return headers_auth(crear_token_mock())


@pytest.fixture
def client(usuario_autenticado):
    def override_get_current_user():
        return usuario_autenticado

    def override_obtener_usuario():
        uc = MagicMock(spec=ObtenerUsuarioUseCase)
        uc.ejecutar.return_value = usuario_autenticado
        return uc

    def override_marcar_leida():
        # Use case REAL sobre un repo mockeado: el aviso por WebSocket vive en el
        # use case, y mockearlo haría que esta suite no probara nada.
        return MarcarNotificacionLeidaUseCase(MagicMock(spec=RepositorioNotificaciones))

    def override_marcar_todas():
        repositorio = MagicMock(spec=RepositorioNotificaciones)
        repositorio.marcar_todas_leidas.return_value = 3
        return MarcarNotificacionesLeidasUseCase(repositorio)

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_obtener_usuario_use_case] = override_obtener_usuario
    app.dependency_overrides[get_marcar_notificacion_leida_use_case] = override_marcar_leida
    app.dependency_overrides[get_marcar_notificaciones_leidas_use_case] = override_marcar_todas

    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestTicketWebSocket:

    def test_emite_ticket_de_un_solo_proposito(self, client, headers_auth_validos):
        response = client.post('/auth/ws-ticket', headers=headers_auth_validos)

        assert response.status_code == 200
        cuerpo = response.json()
        assert cuerpo['expira_en'] > 0

        payload = JwtAuthenticationService().decodificar_token(cuerpo['ticket'])
        assert payload is not None
        assert payload['proposito'] == 'ws'
        assert payload['rut'] == RUT_ADMIN

    def test_sin_permiso_ver_alertas_retorna_403(self, headers_auth_validos):
        app.dependency_overrides[get_current_user] = _usuario_sin_ver_alertas

        from starlette.testclient import TestClient

        with TestClient(app) as cliente:
            response = cliente.post('/auth/ws-ticket', headers=headers_auth_validos)

        app.dependency_overrides.clear()

        assert response.status_code == 403


@pytest.mark.integration
class TestWebSocketNotificaciones:

    def test_sin_ticket_se_cierra_con_1008(self, client):
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect('/ws/notificaciones'):
                pass

        assert excinfo.value.code == 1008

    def test_ticket_sin_proposito_websocket_se_cierra(self, client):
        # Un access token de sesión no sirve para abrir el canal.
        token = JwtAuthenticationService().crear_access_token({'rut': RUT_ADMIN})

        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect(f'/ws/notificaciones?ticket={token}'):
                pass

        assert excinfo.value.code == 1008

    def test_origen_no_permitido_se_cierra(self, client):
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect(
                f'/ws/notificaciones?ticket={_ticket()}',
                headers={'origin': 'http://sitio-malo.test'},
            ):
                pass

        assert excinfo.value.code == 1008

    def test_origen_permitido_conecta(self, client):
        with client.websocket_connect(
            f'/ws/notificaciones?ticket={_ticket()}',
            headers={'origin': 'http://localhost:3000'},
        ) as websocket:
            mensaje = websocket.receive_json()

        assert mensaje['evento'] == EVENTO_CONEXION_ABIERTA

    def test_usuario_sin_permiso_no_conecta(self, client):
        app.dependency_overrides[get_obtener_usuario_use_case] = lambda: MagicMock(
            spec=ObtenerUsuarioUseCase,
            **{'ejecutar.return_value': _usuario_sin_ver_alertas()},
        )

        try:
            with pytest.raises(WebSocketDisconnect) as excinfo:
                with client.websocket_connect(f'/ws/notificaciones?ticket={_ticket(RUT_SIN_PERMISO)}'):
                    pass
        finally:
            app.dependency_overrides[get_obtener_usuario_use_case] = lambda: MagicMock(
                spec=ObtenerUsuarioUseCase,
                **{'ejecutar.return_value': crear_usuario_admin_mock()},
            )

        assert excinfo.value.code == 1008

    def test_publicacion_del_backend_llega_al_cliente(self, client):
        with client.websocket_connect(f'/ws/notificaciones?ticket={_ticket()}') as websocket:
            assert websocket.receive_json()['evento'] == EVENTO_CONEXION_ABIERTA

            hub.publicar_desde_hilo(
                [RUT_ADMIN],
                {'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS, 'motivo': 'alertas_generadas'},
            )

            mensaje = websocket.receive_json()

        assert mensaje == {
            'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS,
            'motivo': 'alertas_generadas',
        }
        assert hub.conexiones_de(RUT_ADMIN) == 0

    def test_desconexion_limpia_el_hub(self, client):
        with client.websocket_connect(f'/ws/notificaciones?ticket={_ticket()}') as websocket:
            websocket.receive_json()
            assert hub.conexiones_de(RUT_ADMIN) == 1

        assert hub.conexiones_de(RUT_ADMIN) == 0

    def test_leer_todas_avisa_al_resto_de_pestanas(self, client, headers_auth_validos):
        # Regresión: "Marcar todas leídas" no refrescaba las demás pestañas
        # porque el endpoint no publicaba en el hub.
        with client.websocket_connect(f'/ws/notificaciones?ticket={_ticket()}') as websocket:
            assert websocket.receive_json()['evento'] == EVENTO_CONEXION_ABIERTA

            response = client.post('/notificaciones/leer-todas', headers=headers_auth_validos)

            assert response.status_code == 200
            assert response.json()['total'] == 3
            mensaje = websocket.receive_json()

        assert mensaje == {
            'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS,
            'motivo': 'marcadas_leidas',
        }

    def test_marcar_leida_avisa_al_resto_de_pestanas(self, client, headers_auth_validos):
        with client.websocket_connect(f'/ws/notificaciones?ticket={_ticket()}') as websocket:
            assert websocket.receive_json()['evento'] == EVENTO_CONEXION_ABIERTA

            response = client.patch('/notificaciones/7/leer', headers=headers_auth_validos)

            assert response.status_code == 200
            mensaje = websocket.receive_json()

        assert mensaje == {
            'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS,
            'motivo': 'marcadas_leidas',
        }
