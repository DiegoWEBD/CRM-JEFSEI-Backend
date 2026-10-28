from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.prospecto_factory import crear_prospecto_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='12345678-9')


@pytest.fixture
def repositorio_usuarios_mock():
    mock = MagicMock(spec=RepositorioUsuarios)
    mock.usuario_tiene_permiso.return_value = True
    return mock


@pytest.fixture
def authorization_service(repositorio_usuarios_mock):
    return AuthorizationService(
        authorization_repository=MagicMock(spec=AuthorizationRepository),
        repositorio_prospectos=MagicMock(spec=RepositorioProspectos),
        repositorio_usuarios=repositorio_usuarios_mock,
    )


@pytest.mark.unit
class TestUsuarioPuedeDescartarProcesoComercial:

    def test_permiso_y_ejecutivo_asignado_permite_descartar(
        self, authorization_service, usuario
    ):
        prospecto = crear_prospecto_mock(
            ejecutivo_comercial_asignado=crear_usuario_mock(rut='12345678-9')
        )

        assert authorization_service.usuario_puede_descartar_proceso_comercial(prospecto, usuario) is True

    def test_sin_permiso_no_permite_descartar(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        repositorio_usuarios_mock.usuario_tiene_permiso.return_value = False
        prospecto = crear_prospecto_mock(
            ejecutivo_comercial_asignado=crear_usuario_mock(rut='12345678-9')
        )

        assert authorization_service.usuario_puede_descartar_proceso_comercial(prospecto, usuario) is False

    def test_consulta_el_permiso_descartar_proceso_comercial(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        prospecto = crear_prospecto_mock(
            ejecutivo_comercial_asignado=crear_usuario_mock(rut='12345678-9')
        )

        authorization_service.usuario_puede_descartar_proceso_comercial(prospecto, usuario)

        repositorio_usuarios_mock.usuario_tiene_permiso.assert_called_once_with(
            usuario, 'DESCARTAR_PROCESO_COMERCIAL'
        )

    def test_sin_ejecutivo_comercial_asignado_no_permite_descartar(
        self, authorization_service, usuario
    ):
        prospecto = crear_prospecto_mock(ejecutivo_comercial_asignado=None)

        assert authorization_service.usuario_puede_descartar_proceso_comercial(prospecto, usuario) is False

    def test_ejecutivo_distinto_al_asignado_no_permite_descartar(
        self, authorization_service, usuario
    ):
        prospecto = crear_prospecto_mock(
            ejecutivo_comercial_asignado=crear_usuario_mock(rut='99999999-9')
        )

        assert authorization_service.usuario_puede_descartar_proceso_comercial(prospecto, usuario) is False
