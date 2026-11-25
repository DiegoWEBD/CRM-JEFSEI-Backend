from unittest.mock import MagicMock

import pytest

from app.aplicacion.evaluacion_proyectos.use_cases.armar_estudio_comercial_condominio import (
    ArmarEstudioComercialCondominioUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.usuario.usuario import Usuario
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.estudio_comercial.deps import get_armar_estudio_comercial_use_case
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock


def _usuario_con_permisos(*codigos: str) -> Usuario:
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


BODY_ESTUDIO = {
    'id_proceso_comercial': 10,
    'monto_asegurado_actual': None,
    'con_monto_sugerido': True,
    'infraseguro_primer_ejemplo': None,
    'infraseguro_segundo_ejemplo': None,
    'cantidad_cuotas': 12,
    'ids_cotizacion': [10],
    'valor_uf': 39000.0,
    'secciones': None,
}

URL = '/estudio-comercial/'


@pytest.fixture
def use_case_mock():
    return MagicMock(spec=ArmarEstudioComercialCondominioUseCase)


@pytest.fixture
def usuario_con_permiso():
    return _usuario_con_permisos('ARMAR_ESTUDIO_COMERCIAL')


@pytest.fixture
def usuario_sin_permisos():
    return _usuario_con_permisos('VER_ESTUDIOS_COMERCIALES_PROPIOS')


def _client(usuario, use_case_mock):
    def override_get_current_user():
        return usuario

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_armar_estudio_comercial_use_case] = lambda: use_case_mock

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_con_permiso(usuario_con_permiso, use_case_mock):
    yield from _client(usuario_con_permiso, use_case_mock)


@pytest.fixture
def client_sin_permiso(usuario_sin_permisos, use_case_mock):
    yield from _client(usuario_sin_permisos, use_case_mock)


@pytest.mark.integration
class TestArmarEstudioComercialEndpoint:

    def test_sin_permiso_retorna_403(self, client_sin_permiso, use_case_mock, headers_auth_validos):
        response = client_sin_permiso.post(URL, json=BODY_ESTUDIO, headers=headers_auth_validos)

        assert response.status_code == 403
        use_case_mock.ejecutar.assert_not_called()

    def test_cotizacion_ajena_retorna_409(self, client_con_permiso, use_case_mock, headers_auth_validos):
        use_case_mock.ejecutar.side_effect = ConflictoEnAccionException(
            'La cotización 10 no pertenece a la oportunidad 10'
        )

        response = client_con_permiso.post(URL, json=BODY_ESTUDIO, headers=headers_auth_validos)

        assert response.status_code == 409

    def test_cotizacion_inexistente_retorna_404(self, client_con_permiso, use_case_mock, headers_auth_validos):
        use_case_mock.ejecutar.side_effect = RecursoNoEncontradoException(
            'Cotización 10 no encontrada'
        )

        response = client_con_permiso.post(URL, json=BODY_ESTUDIO, headers=headers_auth_validos)

        assert response.status_code == 404

    def test_armar_estudio_exitoso_retorna_201(
        self, client_con_permiso, use_case_mock, headers_auth_validos, tmp_path
    ):
        archivo = tmp_path / 'estudio_comercial_condominio_id_5.docx'
        archivo.write_bytes(b'%PDF-1.4\ncontenido de prueba\n')
        use_case_mock.ejecutar.return_value = str(archivo)

        response = client_con_permiso.post(URL, json=BODY_ESTUDIO, headers=headers_auth_validos)

        assert response.status_code == 201
        body = response.json()
        assert 'archivo_base64' in body
        assert body['nombre_archivo'] == 'estudio_comercial_10.docx'
