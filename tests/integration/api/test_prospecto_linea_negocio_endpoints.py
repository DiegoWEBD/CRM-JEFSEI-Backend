from unittest.mock import MagicMock

import pytest

from app.main import app
from app.aplicacion.prospecto.use_cases.cambiar_linea_negocio_prospecto import (
    CambiarLineaNegocioProspectoUseCase,
)
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.usuario.usuario import Usuario
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.prospecto.dependencias.deps import (
    get_actualizar_linea_negocio_prospecto_use_case,
)
from tests.integration.api.conftest_api import *  # noqa: F401,F403
from tests.factories.usuario_factory import crear_permiso_mock, crear_rol_mock, crear_usuario_mock
from tests.factories.auth_factory import crear_token_mock, headers_auth


def _usuario_con_permisos(*codigos: str) -> Usuario:
    permisos = [crear_permiso_mock(codigo=codigo, descripcion=codigo) for codigo in codigos]
    return crear_usuario_mock(roles=[crear_rol_mock(permisos=permisos)])


@pytest.fixture
def usuario_cambiar_linea():
    return _usuario_con_permisos("CAMBIAR_LINEA_NEGOCIO_PROSPECTO")


@pytest.fixture
def usuario_sin_permiso():
    return _usuario_con_permisos("ACTUALIZAR_DATOS_PROSPECTO")


@pytest.fixture
def use_case_mock():
    mock = MagicMock(spec=CambiarLineaNegocioProspectoUseCase)
    mock.ejecutar.return_value = 2
    return mock


@pytest.fixture
def client_cambiar_linea(usuario_cambiar_linea, use_case_mock):
    def override_get_current_user():
        return usuario_cambiar_linea

    def override_use_case():
        return use_case_mock

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_actualizar_linea_negocio_prospecto_use_case] = override_use_case

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def client_sin_permiso(usuario_sin_permiso, use_case_mock):
    def override_get_current_user():
        return usuario_sin_permiso

    def override_use_case():
        return use_case_mock

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_actualizar_linea_negocio_prospecto_use_case] = override_use_case

    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.integration
class TestCambiarLineaNegocioProspectoEndpoints:

    def test_cambio_exitoso_retorna_200_con_conteo(
        self, client_cambiar_linea, use_case_mock, usuario_cambiar_linea, headers_auth_validos
    ):
        response = client_cambiar_linea.patch(
            "/prospectos/1/linea-negocio",
            json={"id_linea_negocio": 2},
            headers=headers_auth_validos,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Línea de negocio del prospecto actualizada correctamente"
        assert body["oportunidades_descartadas"] == 2
        use_case_mock.ejecutar.assert_called_once()
        kwargs = use_case_mock.ejecutar.call_args.kwargs
        assert kwargs["id"] == 1
        assert kwargs["id_linea_negocio"] == 2
        assert kwargs["usuario"] is usuario_cambiar_linea

    def test_sin_permiso_cambiar_linea_retorna_403(
        self, client_sin_permiso, use_case_mock, headers_auth_validos
    ):
        response = client_sin_permiso.patch(
            "/prospectos/1/linea-negocio",
            json={"id_linea_negocio": 2},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403
        use_case_mock.ejecutar.assert_not_called()

    def test_no_autenticado_retorna_401(self, use_case_mock):
        from starlette.testclient import TestClient
        app.dependency_overrides[get_actualizar_linea_negocio_prospecto_use_case] = lambda: use_case_mock
        try:
            with TestClient(app) as c:
                response = c.patch(
                    "/prospectos/1/linea-negocio",
                    json={"id_linea_negocio": 2},
                )
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.auth
    def test_no_es_el_ejecutivo_asignado_retorna_403(
        self, client_cambiar_linea, use_case_mock, headers_auth_validos
    ):
        use_case_mock.ejecutar.side_effect = UsuarioNoAutorizadoException(
            "Solo el ejecutivo comercial asignado puede cambiar la línea de negocio del prospecto"
        )

        response = client_cambiar_linea.patch(
            "/prospectos/1/linea-negocio",
            json={"id_linea_negocio": 2},
            headers=headers_auth_validos,
        )

        assert response.status_code == 403

    def test_prospecto_no_encontrado_retorna_404(
        self, client_cambiar_linea, use_case_mock, headers_auth_validos
    ):
        use_case_mock.ejecutar.side_effect = RecursoNoEncontradoException("Prospecto no encontrado")

        response = client_cambiar_linea.patch(
            "/prospectos/999/linea-negocio",
            json={"id_linea_negocio": 2},
            headers=headers_auth_validos,
        )

        assert response.status_code == 404

    def test_linea_de_negocio_inexistente_retorna_400(
        self, client_cambiar_linea, use_case_mock, headers_auth_validos
    ):
        use_case_mock.ejecutar.side_effect = DatoInvalidoException(
            "La línea de negocio indicada no existe"
        )

        response = client_cambiar_linea.patch(
            "/prospectos/1/linea-negocio",
            json={"id_linea_negocio": 999},
            headers=headers_auth_validos,
        )

        assert response.status_code == 400

    def test_misma_linea_de_negocio_retorna_409(
        self, client_cambiar_linea, use_case_mock, headers_auth_validos
    ):
        use_case_mock.ejecutar.side_effect = ConflictoEnAccionException(
            "El prospecto ya pertenece a la línea de negocio indicada"
        )

        response = client_cambiar_linea.patch(
            "/prospectos/1/linea-negocio",
            json={"id_linea_negocio": 1},
            headers=headers_auth_validos,
        )

        assert response.status_code == 409

    def test_id_linea_negocio_invalido_retorna_422(
        self, client_cambiar_linea, use_case_mock, headers_auth_validos
    ):
        response = client_cambiar_linea.patch(
            "/prospectos/1/linea-negocio",
            json={"id_linea_negocio": "no-numero"},
            headers=headers_auth_validos,
        )

        assert response.status_code == 422
        use_case_mock.ejecutar.assert_not_called()
