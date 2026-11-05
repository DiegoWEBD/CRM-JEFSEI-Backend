from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.authorization.authorizacion_repository import AuthorizationRepository
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.solicitud_cotizacion.repositorio_solicitudes_cotizacion import RepositorioSolicitudesCotizacion
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock
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
        repositorio_procesos_comerciales=MagicMock(spec=RepositorioProcesosComerciales),
        repositorio_solicitudes_cotizacion=MagicMock(spec=RepositorioSolicitudesCotizacion),
    )


@pytest.mark.unit
class TestUsuarioPuedeDescartarProcesoComercial:

    def test_permiso_y_ejecutivo_asignado_permite_descartar(
        self, authorization_service, usuario
    ):
        oportunidad = crear_proceso_comercial_mock(
            ejecutivo_comercial=crear_usuario_mock(rut='12345678-9')
        )

        assert authorization_service.usuario_puede_descartar_proceso_comercial(oportunidad, usuario) is True

    def test_sin_permiso_no_permite_descartar(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        repositorio_usuarios_mock.usuario_tiene_permiso.return_value = False
        oportunidad = crear_proceso_comercial_mock(
            ejecutivo_comercial=crear_usuario_mock(rut='12345678-9')
        )

        assert authorization_service.usuario_puede_descartar_proceso_comercial(oportunidad, usuario) is False

    def test_consulta_el_permiso_descartar_proceso_comercial(
        self, authorization_service, repositorio_usuarios_mock, usuario
    ):
        oportunidad = crear_proceso_comercial_mock(
            ejecutivo_comercial=crear_usuario_mock(rut='12345678-9')
        )

        authorization_service.usuario_puede_descartar_proceso_comercial(oportunidad, usuario)

        repositorio_usuarios_mock.usuario_tiene_permiso.assert_called_once_with(
            usuario, 'DESCARTAR_PROCESO_COMERCIAL'
        )

    def test_sin_ejecutivo_comercial_asignado_no_permite_descartar(
        self, authorization_service, usuario
    ):
        oportunidad = crear_proceso_comercial_mock(ejecutivo_comercial=None)

        assert authorization_service.usuario_puede_descartar_proceso_comercial(oportunidad, usuario) is False

    def test_ejecutivo_distinto_al_asignado_no_permite_descartar(
        self, authorization_service, usuario
    ):
        oportunidad = crear_proceso_comercial_mock(
            ejecutivo_comercial=crear_usuario_mock(rut='99999999-9')
        )

        assert authorization_service.usuario_puede_descartar_proceso_comercial(oportunidad, usuario) is False

    def test_renovacion_permite_con_ejecutivo_de_renovacion_asignado(
        self, authorization_service, usuario
    ):
        oportunidad = crear_proceso_comercial_mock(
            renovacion=True,
            ejecutivo_renovacion=crear_usuario_mock(rut='12345678-9'),
        )

        assert authorization_service.usuario_puede_descartar_proceso_comercial(oportunidad, usuario) is True

    def test_renovacion_con_ejecutivo_de_renovacion_distinto_no_permite(
        self, authorization_service, usuario
    ):
        oportunidad = crear_proceso_comercial_mock(
            renovacion=True,
            ejecutivo_renovacion=crear_usuario_mock(rut='99999999-9'),
        )

        assert authorization_service.usuario_puede_descartar_proceso_comercial(oportunidad, usuario) is False

    def test_renovacion_sin_ejecutivo_de_renovacion_no_permite(
        self, authorization_service, usuario
    ):
        oportunidad = crear_proceso_comercial_mock(
            renovacion=True,
            ejecutivo_renovacion=None,
            ejecutivo_comercial=crear_usuario_mock(rut='12345678-9'),
        )

        assert authorization_service.usuario_puede_descartar_proceso_comercial(oportunidad, usuario) is False
