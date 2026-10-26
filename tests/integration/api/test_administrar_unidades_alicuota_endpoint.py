import pytest
from unittest.mock import MagicMock

from app.aplicacion.proceso_comercial.use_cases.administrar_unidades_alicuota import (
    SIN_CAMBIO,
    AdministrarUnidadesAlicuotaUseCase,
)
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.proceso_comercial.dependencias.deps import (
    get_administrar_unidades_alicuota_use_case,
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

    uc = MagicMock(spec=AdministrarUnidadesAlicuotaUseCase)
    uc.ejecutar.return_value = [
        UnidadAlicuota(
            identificador_unidad='Depto 1',
            prorrateo=0.025,
            fila_origen=2,
            id=7,
            descartada=True,
            monto_asegurado_personalizado=None,
        ),
        UnidadAlicuota(
            identificador_unidad='Depto 2',
            prorrateo=0.05,
            fila_origen=3,
            id=8,
            descartada=False,
            monto_asegurado_personalizado=1500.0,
        ),
    ]

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_administrar_unidades_alicuota_use_case] = lambda: uc

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
class TestActualizarUnidadesAlicuotaEndpoint:

    def test_actualiza_varias_unidades_en_un_solo_request(self, client_administrar, headers_auth_validos):
        client, uc = client_administrar

        response = client.patch(
            '/procesos-comerciales/42/alicuota/unidades',
            json={
                'unidades': [
                    {'id_unidad': 7, 'descartada': True},
                    {'id_unidad': 8, 'monto_asegurado_personalizado': 1500},
                ]
            },
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        body = response.json()
        assert body['cantidad'] == 2
        assert [unidad['id'] for unidad in body['unidades']] == [7, 8]
        assert body['unidades'][0]['descartada'] is True
        assert body['unidades'][1]['monto_asegurado_personalizado'] == 1500.0

        kwargs = uc.ejecutar.call_args.kwargs
        assert kwargs['id_proceso_comercial'] == 42

        cambios = kwargs['cambios']
        assert [cambio.id_unidad for cambio in cambios] == [7, 8]
        assert cambios[0].descartada is True
        assert cambios[0].monto_asegurado_personalizado is SIN_CAMBIO
        assert cambios[1].descartada is SIN_CAMBIO
        assert cambios[1].monto_asegurado_personalizado == 1500.0

    def test_monto_nulo_vuelve_al_sugerido(self, client_administrar, headers_auth_validos):
        client, uc = client_administrar

        response = client.patch(
            '/procesos-comerciales/42/alicuota/unidades',
            json={'unidades': [{'id_unidad': 7, 'monto_asegurado_personalizado': None}]},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        cambios = uc.ejecutar.call_args.kwargs['cambios']
        assert cambios[0].monto_asegurado_personalizado is None
        assert cambios[0].descartada is SIN_CAMBIO

    def test_campos_no_informados_no_se_marcan_como_cambio(self, client_administrar, headers_auth_validos):
        client, uc = client_administrar

        response = client.patch(
            '/procesos-comerciales/42/alicuota/unidades',
            json={'unidades': [{'id_unidad': 7}]},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        cambios = uc.ejecutar.call_args.kwargs['cambios']
        assert cambios[0].descartada is SIN_CAMBIO
        assert cambios[0].monto_asegurado_personalizado is SIN_CAMBIO

    def test_unidades_es_requerido(self, client_administrar, headers_auth_validos):
        client, _ = client_administrar

        response = client.patch(
            '/procesos-comerciales/42/alicuota/unidades',
            json={},
            headers=headers_auth_validos,
        )

        assert response.status_code == 422

    def test_sin_permiso_es_rechazado(self, client_administrar_sin_permiso, headers_auth_validos):
        response = client_administrar_sin_permiso.patch(
            '/procesos-comerciales/42/alicuota/unidades',
            json={'unidades': [{'id_unidad': 7, 'descartada': True}]},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
