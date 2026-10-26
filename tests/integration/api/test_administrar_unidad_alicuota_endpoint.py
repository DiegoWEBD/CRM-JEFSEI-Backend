import pytest
from unittest.mock import MagicMock

from app.aplicacion.proceso_comercial.use_cases.administrar_unidad_alicuota import (
    SIN_CAMBIO,
    AdministrarUnidadAlicuotaUseCase,
)
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.proceso_comercial.dependencias.deps import (
    get_administrar_unidad_alicuota_use_case,
)
from tests.factories.auth_factory import crear_token_mock, headers_auth
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock


def _usuario_con_permisos(*permisos: str):
    return crear_usuario_mock(
        roles=[crear_rol_mock(
            codigo='EJECUTIVO_EVALUACION',
            nombre='Ejecutivo de evaluación',
            permisos=[crear_permiso_mock(codigo=codigo) for codigo in permisos],
        )],
    )


@pytest.fixture
def token_valido():
    return crear_token_mock()


@pytest.fixture
def headers_auth_validos(token_valido):
    return headers_auth(token_valido)


@pytest.fixture
def client_administrar():
    usuario = _usuario_con_permisos('ADMINISTRAR_ALICUOTAS')

    def override_get_current_user():
        return usuario

    uc = MagicMock(spec=AdministrarUnidadAlicuotaUseCase)
    uc.ejecutar.return_value = UnidadAlicuota(
        identificador_unidad='Depto 1',
        prorrateo=0.025,
        fila_origen=2,
        id=7,
        descartada=True,
        monto_asegurado_personalizado=1500.0,
    )

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_administrar_unidad_alicuota_use_case] = lambda: uc

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c, uc

    app.dependency_overrides.clear()


@pytest.fixture
def client_administrar_sin_permiso():
    usuario = crear_usuario_mock(
        roles=[crear_rol_mock(permisos=[crear_permiso_mock(codigo='VER_ALERTAS')])]
    )

    def override_get_current_user():
        return usuario

    app.dependency_overrides[get_current_user] = override_get_current_user

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestActualizarUnidadAlicuotaEndpoint:

    def test_descarta_una_unidad(self, client_administrar, headers_auth_validos):
        client, uc = client_administrar

        response = client.patch(
            '/procesos-comerciales/42/alicuota/unidades/7',
            json={'descartada': True},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        body = response.json()
        assert body['unidad']['id'] == 7
        assert body['unidad']['descartada'] is True

        kwargs = uc.ejecutar.call_args.kwargs
        assert kwargs['id_proceso_comercial'] == 42
        assert kwargs['id_unidad'] == 7
        assert kwargs['descartada'] is True
        assert kwargs['monto_asegurado_personalizado'] is SIN_CAMBIO

    def test_fija_monto_personalizado(self, client_administrar, headers_auth_validos):
        client, uc = client_administrar

        response = client.patch(
            '/procesos-comerciales/42/alicuota/unidades/7',
            json={'monto_asegurado_personalizado': 1500},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        kwargs = uc.ejecutar.call_args.kwargs
        assert kwargs['monto_asegurado_personalizado'] == 1500.0
        assert kwargs['descartada'] is SIN_CAMBIO

    def test_monto_nulo_vuelve_al_sugerido(self, client_administrar, headers_auth_validos):
        client, uc = client_administrar

        response = client.patch(
            '/procesos-comerciales/42/alicuota/unidades/7',
            json={'monto_asegurado_personalizado': None},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        assert uc.ejecutar.call_args.kwargs['monto_asegurado_personalizado'] is None

    def test_sin_permiso_es_rechazado(self, client_administrar_sin_permiso, headers_auth_validos):
        response = client_administrar_sin_permiso.patch(
            '/procesos-comerciales/42/alicuota/unidades/7',
            json={'descartada': True},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
