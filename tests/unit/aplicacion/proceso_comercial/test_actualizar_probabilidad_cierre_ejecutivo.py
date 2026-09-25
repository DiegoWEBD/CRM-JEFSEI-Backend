from unittest.mock import MagicMock

import pytest

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.proceso_comercial.use_cases.actualizar_probabilidad_cierre_ejecutivo import ActualizarProbabilidadCierreEjecutivoUseCase
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
    return ActualizarProbabilidadCierreEjecutivoUseCase(
        authorization_service=authorization_service_mock,
        repositorio_procesos_comerciales=repositorio_mock,
    )


@pytest.mark.unit
class TestActualizarProbabilidadCierreEjecutivoUseCase:

    def test_actualizar_exitoso(self, use_case, repositorio_mock, authorization_service_mock):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=False)
        authorization_service_mock.usuario_puede_actualizar_probabilidad_cierre.return_value = True

        use_case.ejecutar(id=1, probabilidad_cierre_ejecutivo=0.75, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_probabilidad_cierre_ejecutivo.assert_called_once_with(
            id=1, probabilidad=0.75
        )

    def test_actualizar_con_null_limpia_el_campo(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=False)
        authorization_service_mock.usuario_puede_actualizar_probabilidad_cierre.return_value = True

        use_case.ejecutar(id=1, probabilidad_cierre_ejecutivo=None, usuario=crear_usuario_mock())

        repositorio_mock.actualizar_probabilidad_cierre_ejecutivo.assert_called_once_with(
            id=1, probabilidad=None
        )

    def test_proceso_no_encontrado_lanza_excepcion(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(
                id=99,
                probabilidad_cierre_ejecutivo=None,
                usuario=crear_usuario_mock(),
            )

        authorization_service_mock.usuario_puede_actualizar_probabilidad_cierre.assert_not_called()
        repositorio_mock.actualizar_probabilidad_cierre_ejecutivo.assert_not_called()

    def test_sin_autorizacion_lanza_excepcion(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=False)
        authorization_service_mock.usuario_puede_actualizar_probabilidad_cierre.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(
                id=1,
                probabilidad_cierre_ejecutivo=None,
                usuario=crear_usuario_mock(),
            )

        repositorio_mock.actualizar_probabilidad_cierre_ejecutivo.assert_not_called()

    def test_proceso_cerrado_lanza_conflicto(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=True)
        authorization_service_mock.usuario_puede_actualizar_probabilidad_cierre.return_value = True

        with pytest.raises(ConflictoEnAccionException):
            use_case.ejecutar(
                id=1,
                probabilidad_cierre_ejecutivo=None,
                usuario=crear_usuario_mock(),
            )

        repositorio_mock.actualizar_probabilidad_cierre_ejecutivo.assert_not_called()

    def test_autorizacion_se_verifica_antes_del_estado_cerrado(
        self, use_case, repositorio_mock, authorization_service_mock
    ):
        repositorio_mock.buscar.return_value = crear_proceso_comercial_mock(cerrado=True)
        authorization_service_mock.usuario_puede_actualizar_probabilidad_cierre.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(
                id=1,
                probabilidad_cierre_ejecutivo=None,
                usuario=crear_usuario_mock(),
            )

        repositorio_mock.actualizar_probabilidad_cierre_ejecutivo.assert_not_called()
