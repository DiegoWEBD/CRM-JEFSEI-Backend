from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.prospecto_factory import crear_prospecto_mock
from tests.factories.usuario_factory import crear_usuario_mock

PERMISO_TODOS = 'ESTABLECER_DEPRECIACION_PERSONALIZADA_TODOS'
PERMISO_PROPIOS = 'ESTABLECER_DEPRECIACION_PERSONALIZADA_PROPIOS'


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='12345678-9')


@pytest.fixture
def repositorio_usuarios_mock():
    mock = MagicMock(spec=RepositorioUsuarios)
    mock.usuario_tiene_permiso.return_value = False
    return mock


@pytest.fixture
def authorization_service(repositorio_usuarios_mock):
    return AuthorizationService(
        authorization_repository=MagicMock(spec=AuthorizationRepository),
        repositorio_prospectos=MagicMock(spec=RepositorioProspectos),
        repositorio_usuarios=repositorio_usuarios_mock,
    )


def _con_permiso(repositorio_usuarios_mock, *codigos):
    repositorio_usuarios_mock.usuario_tiene_permiso.side_effect = (
        lambda usuario, codigo: codigo in codigos
    )


@pytest.mark.unit
class TestUsuarioPuedeEstablecerDepreciacionPersonalizada:

    def test_permiso_todos_permite_cualquier_prospecto(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_TODOS)
        prospecto = crear_prospecto_mock(
            ejecutivo_evaluacion_asignado=crear_usuario_mock(rut='99999999-9')
        )

        assert authorization_service.usuario_puede_establecer_depreciacion_personalizada(prospecto, usuario) is True

    def test_permiso_todos_permite_sin_ejecutivo_asignado(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_TODOS)
        prospecto = crear_prospecto_mock(ejecutivo_evaluacion_asignado=None)

        assert authorization_service.usuario_puede_establecer_depreciacion_personalizada(prospecto, usuario) is True

    def test_permiso_propios_con_ejecutivo_asignado_permite(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_PROPIOS)
        prospecto = crear_prospecto_mock(
            ejecutivo_evaluacion_asignado=crear_usuario_mock(rut='12345678-9')
        )

        assert authorization_service.usuario_puede_establecer_depreciacion_personalizada(prospecto, usuario) is True

    def test_permiso_propios_con_ejecutivo_distinto_no_permite(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_PROPIOS)
        prospecto = crear_prospecto_mock(
            ejecutivo_evaluacion_asignado=crear_usuario_mock(rut='99999999-9')
        )

        assert authorization_service.usuario_puede_establecer_depreciacion_personalizada(prospecto, usuario) is False

    def test_permiso_propios_sin_ejecutivo_asignado_no_permite(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_PROPIOS)
        prospecto = crear_prospecto_mock(ejecutivo_evaluacion_asignado=None)

        assert authorization_service.usuario_puede_establecer_depreciacion_personalizada(prospecto, usuario) is False

    def test_sin_permisos_no_permite(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock)
        prospecto = crear_prospecto_mock(
            ejecutivo_evaluacion_asignado=crear_usuario_mock(rut='12345678-9')
        )

        assert authorization_service.usuario_puede_establecer_depreciacion_personalizada(prospecto, usuario) is False

    def test_ambos_permisos_no_exige_asignacion(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        _con_permiso(repositorio_usuarios_mock, PERMISO_TODOS, PERMISO_PROPIOS)
        prospecto = crear_prospecto_mock(
            ejecutivo_evaluacion_asignado=crear_usuario_mock(rut='99999999-9')
        )

        assert authorization_service.usuario_puede_establecer_depreciacion_personalizada(prospecto, usuario) is True
