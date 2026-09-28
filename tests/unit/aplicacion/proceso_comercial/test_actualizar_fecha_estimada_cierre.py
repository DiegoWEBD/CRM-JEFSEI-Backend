from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.actualizar_fecha_estimada_cierre import ActualizarFechaEstimadaCierreUseCase
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import RepositorioProcesosComerciales
from tests.factories.proceso_comercial_factory import crear_proceso_comercial_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioProcesosComerciales)


@pytest.fixture
def authorization_service_mock():
    return MagicMock(spec=AuthorizationService)


@pytest.fixture
def use_case(repositorio_mock, authorization_service_mock):
    return ActualizarFechaEstimadaCierreUseCase(
        authorization_service=authorization_service_mock,
        repositorio_procesos_comerciales=repositorio_mock,
    )


@pytest.mark.unit
class TestActualizarFechaEstimadaCierreUseCase:

    def test_actualizar_exitoso(self, use_case, repositorio_mock, authorization_service_mock):
        proceso = crear_proceso_comercial_mock(cerrado=False)
        repositorio_mock.buscar.return_value = proceso
        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.return_value = True
        fecha = datetime(2026, 10, 15, 0, 0, 0, tzinfo=timezone.utc)

        use_case.ejecutar(id=1, fecha_estimada_cierre=fecha, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_called_once_with(
            id=1, fecha=fecha
        )

    def test_actualizar_con_fecha_null_limpia_el_campo(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=False)
        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.return_value = True

        use_case.ejecutar(id=1, fecha_estimada_cierre=None, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_called_once_with(
            id=1, fecha=None
        )

    def test_proceso_no_encontrado_lanza_excepcion(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(
                id=99,
                fecha_estimada_cierre=None,
                usuario=crear_usuario_mock(),
            )

        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.assert_not_called()
        repositorio_mock.actualizar_fecha_estimada_cierre.assert_not_called()

    def test_sin_autorizacion_lanza_excepcion(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=False)
        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(
                id=1,
                fecha_estimada_cierre=None,
                usuario=crear_usuario_mock(),
            )

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_not_called()

    def test_proceso_cerrado_lanza_conflicto(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=True)
        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.return_value = True

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(
                id=1,
                fecha_estimada_cierre=None,
                usuario=crear_usuario_mock(),
            )

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_not_called()

    def test_autorizacion_se_verifica_antes_del_estado_cerrado(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=True)
        authorization_service_mock.usuario_puede_actualizar_fecha_estimada_cierre.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(
                id=1,
                fecha_estimada_cierre=None,
                usuario=crear_usuario_mock(),
            )

        repositorio_mock.actualizar_fecha_estimada_cierre.assert_not_called()
