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

RUT_USUARIO = '12345678-9'


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut=RUT_USUARIO)


@pytest.fixture
def repositorio_usuarios_mock():
    return MagicMock(spec=RepositorioUsuarios)


@pytest.fixture
def repositorio_solicitudes_mock():
    return MagicMock(spec=RepositorioSolicitudesCotizacion)


@pytest.fixture
def repositorio_procesos_mock():
    return MagicMock(spec=RepositorioProcesosComerciales)


@pytest.fixture
def authorization_service(
    repositorio_usuarios_mock,
    repositorio_solicitudes_mock,
    repositorio_procesos_mock,
):
    return AuthorizationService(
        authorization_repository=MagicMock(spec=AuthorizationRepository),
        repositorio_prospectos=MagicMock(spec=RepositorioProspectos),
        repositorio_usuarios=repositorio_usuarios_mock,
        repositorio_procesos_comerciales=repositorio_procesos_mock,
        repositorio_solicitudes_cotizacion=repositorio_solicitudes_mock,
    )


def _con_permisos(repositorio_usuarios_mock, *codigos):
    codigos_permiso = set(codigos)
    repositorio_usuarios_mock.usuario_tiene_permiso.side_effect = (
        lambda usuario, codigo_permiso: codigo_permiso in codigos_permiso
    )


@pytest.mark.unit
class TestUsuarioPuedeVerEstudiosComerciales:

    def test_permiso_global_retorna_true(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_TODOS')

        resultado = authorization_service.usuario_puede_ver_estudios_comerciales(usuario, 1)

        assert resultado is True
        repositorio_solicitudes_mock.buscar.assert_not_called()

    def test_propios_y_comercial_asignado_retorna_true(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            ejecutivo_comercial=crear_usuario_mock(rut=RUT_USUARIO),
        )

        resultado = authorization_service.usuario_puede_ver_estudios_comerciales(usuario, 1)

        assert resultado is True
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.assert_called_once_with(1)

    def test_propios_y_evaluador_asignado_retorna_true(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            ejecutivo_evaluacion=crear_usuario_mock(rut=RUT_USUARIO),
        )

        resultado = authorization_service.usuario_puede_ver_estudios_comerciales(usuario, 1)

        assert resultado is True

    def test_propios_pero_no_asignado_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            ejecutivo_comercial=crear_usuario_mock(rut='99999999-9'),
            ejecutivo_evaluacion=crear_usuario_mock(rut='88888888-8'),
        )

        resultado = authorization_service.usuario_puede_ver_estudios_comerciales(usuario, 1)

        assert resultado is False

    def test_sin_permiso_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, usuario,
    ):
        repositorio_usuarios_mock.usuario_tiene_permiso.return_value = False

        resultado = authorization_service.usuario_puede_ver_estudios_comerciales(usuario, 1)

        assert resultado is False
        repositorio_solicitudes_mock.buscar.assert_not_called()

    def test_solicitud_inexistente_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = None

        resultado = authorization_service.usuario_puede_ver_estudios_comerciales(usuario, 999)

        assert resultado is False
        repositorio_solicitudes_mock.buscar.assert_called_once_with(999)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.assert_not_called()

    def test_proceso_inexistente_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = None

        resultado = authorization_service.usuario_puede_ver_estudios_comerciales(usuario, 1)

        assert resultado is False

    def test_renovacion_con_ejecutivo_asignado_retorna_true(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            renovacion=True,
            ejecutivo_renovacion=crear_usuario_mock(rut=RUT_USUARIO),
        )

        resultado = authorization_service.usuario_puede_ver_estudios_comerciales(usuario, 1)

        assert resultado is True

    def test_renovacion_sin_ejecutivo_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            renovacion=True,
            ejecutivo_renovacion=None,
        )

        resultado = authorization_service.usuario_puede_ver_estudios_comerciales(usuario, 1)

        assert resultado is False


@pytest.mark.unit
class TestUsuarioPuedeDescargarEstudioComercial:

    def test_permiso_global_retorna_true(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_TODOS')

        resultado = authorization_service.usuario_puede_descargar_estudio_comercial(usuario, 1)

        assert resultado is True
        repositorio_solicitudes_mock.buscar.assert_not_called()

    def test_propios_y_comercial_asignado_retorna_true(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            ejecutivo_comercial=crear_usuario_mock(rut=RUT_USUARIO),
        )

        resultado = authorization_service.usuario_puede_descargar_estudio_comercial(usuario, 1)

        assert resultado is True
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.assert_called_once_with(1)

    def test_propios_y_evaluador_asignado_retorna_true(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            ejecutivo_evaluacion=crear_usuario_mock(rut=RUT_USUARIO),
        )

        resultado = authorization_service.usuario_puede_descargar_estudio_comercial(usuario, 1)

        assert resultado is True

    def test_propios_pero_no_asignado_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            ejecutivo_comercial=crear_usuario_mock(rut='99999999-9'),
            ejecutivo_evaluacion=crear_usuario_mock(rut='88888888-8'),
        )

        resultado = authorization_service.usuario_puede_descargar_estudio_comercial(usuario, 1)

        assert resultado is False

    def test_sin_permiso_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, usuario,
    ):
        repositorio_usuarios_mock.usuario_tiene_permiso.return_value = False

        resultado = authorization_service.usuario_puede_descargar_estudio_comercial(usuario, 1)

        assert resultado is False
        repositorio_solicitudes_mock.buscar.assert_not_called()

    def test_solicitud_inexistente_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = None

        resultado = authorization_service.usuario_puede_descargar_estudio_comercial(usuario, 999)

        assert resultado is False
        repositorio_solicitudes_mock.buscar.assert_called_once_with(999)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.assert_not_called()

    def test_proceso_inexistente_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = None

        resultado = authorization_service.usuario_puede_descargar_estudio_comercial(usuario, 1)

        assert resultado is False

    def test_renovacion_con_ejecutivo_asignado_retorna_true(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            renovacion=True,
            ejecutivo_renovacion=crear_usuario_mock(rut=RUT_USUARIO),
        )

        resultado = authorization_service.usuario_puede_descargar_estudio_comercial(usuario, 1)

        assert resultado is True

    def test_renovacion_sin_ejecutivo_retorna_false(
        self, authorization_service, repositorio_usuarios_mock,
        repositorio_solicitudes_mock, repositorio_procesos_mock, usuario,
    ):
        _con_permisos(repositorio_usuarios_mock, 'VER_ESTUDIOS_COMERCIALES_PROPIOS')
        repositorio_solicitudes_mock.buscar.return_value = MagicMock(id=1)
        repositorio_procesos_mock.buscar_por_solicitud_cotizacion.return_value = crear_proceso_comercial_mock(
            renovacion=True,
            ejecutivo_renovacion=None,
        )

        resultado = authorization_service.usuario_puede_descargar_estudio_comercial(usuario, 1)

        assert resultado is False
