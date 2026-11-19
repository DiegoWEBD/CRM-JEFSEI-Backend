import pytest
from unittest.mock import MagicMock

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.recordatorio.use_cases.actualizar_recordatorio import ActualizarRecordatorioUseCase
from app.aplicacion.recordatorio.use_cases.completar_recordatorio import CompletarRecordatorioUseCase
from app.aplicacion.recordatorio.use_cases.eliminar_recordatorio import EliminarRecordatorioUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_recordatorios_mock():
    return MagicMock(spec=RepositorioRecordatorios)


@pytest.fixture
def authorization_service_mock():
    return MagicMock(spec=AuthorizationService)


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='11111111-1')


def _use_case_actualizar(repositorio, authorization_service):
    return ActualizarRecordatorioUseCase(repositorio, authorization_service)


def _ejecutar_actualizar(use_case, usuario, **kwargs):
    parametros = {
        'usuario': usuario,
        'id': 1,
        'titulo': 'Recordatorio actualizado',
        'detalle': None,
        'prioridad': 'MEDIA',
        'tipo_gestion': 'LLAMADA',
        'fecha_recordatorio': '2026-12-01T10:00:00',
        'id_prospecto': None,
    }
    parametros.update(kwargs)
    return use_case.ejecutar(**parametros)


@pytest.mark.unit
class TestActualizarRecordatorioUseCase:

    def test_recordatorio_inexistente_retorna_404(
        self, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        repositorio_recordatorios_mock.buscar_propietarios.return_value = None
        use_case = _use_case_actualizar(repositorio_recordatorios_mock, authorization_service_mock)

        with pytest.raises(RecursoNoEncontradoException):
            _ejecutar_actualizar(use_case, usuario)

        repositorio_recordatorios_mock.actualizar.assert_not_called()

    def test_sin_autorizacion_retorna_403(
        self, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['22222222-2']
        authorization_service_mock.usuario_puede_gestionar_recordatorio.return_value = False
        use_case = _use_case_actualizar(repositorio_recordatorios_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            _ejecutar_actualizar(use_case, usuario)

        authorization_service_mock.usuario_puede_gestionar_recordatorio.assert_called_once_with(usuario, 1)
        repositorio_recordatorios_mock.actualizar.assert_not_called()

    def test_con_autorizacion_actualiza(
        self, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['11111111-1']
        authorization_service_mock.usuario_puede_gestionar_recordatorio.return_value = True
        use_case = _use_case_actualizar(repositorio_recordatorios_mock, authorization_service_mock)

        _ejecutar_actualizar(use_case, usuario, titulo='Otro titulo')

        repositorio_recordatorios_mock.actualizar.assert_called_once_with(
            id=1,
            titulo='Otro titulo',
            detalle=None,
            prioridad='MEDIA',
            tipo_gestion='LLAMADA',
            fecha_recordatorio='2026-12-01T10:00:00',
            id_prospecto=None,
        )


@pytest.mark.unit
class TestCompletarRecordatorioUseCase:

    def test_recordatorio_inexistente_retorna_404(
        self, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        repositorio_recordatorios_mock.buscar_propietarios.return_value = None
        use_case = CompletarRecordatorioUseCase(repositorio_recordatorios_mock, authorization_service_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(usuario=usuario, id=1)

        repositorio_recordatorios_mock.completar.assert_not_called()

    def test_sin_autorizacion_retorna_403(
        self, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['22222222-2']
        authorization_service_mock.usuario_puede_gestionar_recordatorio.return_value = False
        use_case = CompletarRecordatorioUseCase(repositorio_recordatorios_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario, id=1)

        repositorio_recordatorios_mock.completar.assert_not_called()

    def test_con_autorizacion_completa(
        self, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['11111111-1']
        authorization_service_mock.usuario_puede_gestionar_recordatorio.return_value = True
        use_case = CompletarRecordatorioUseCase(repositorio_recordatorios_mock, authorization_service_mock)

        use_case.ejecutar(usuario=usuario, id=1)

        repositorio_recordatorios_mock.completar.assert_called_once_with(id=1)


@pytest.mark.unit
class TestEliminarRecordatorioUseCase:

    def test_recordatorio_inexistente_retorna_404(
        self, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        repositorio_recordatorios_mock.buscar_propietarios.return_value = None
        use_case = EliminarRecordatorioUseCase(repositorio_recordatorios_mock, authorization_service_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(usuario=usuario, id=1)

        repositorio_recordatorios_mock.eliminar.assert_not_called()

    def test_sin_autorizacion_retorna_403(
        self, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['22222222-2']
        authorization_service_mock.usuario_puede_gestionar_recordatorio.return_value = False
        use_case = EliminarRecordatorioUseCase(repositorio_recordatorios_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario, id=1)

        repositorio_recordatorios_mock.eliminar.assert_not_called()

    def test_con_autorizacion_elimina(
        self, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        repositorio_recordatorios_mock.buscar_propietarios.return_value = ['11111111-1']
        authorization_service_mock.usuario_puede_gestionar_recordatorio.return_value = True
        use_case = EliminarRecordatorioUseCase(repositorio_recordatorios_mock, authorization_service_mock)

        use_case.ejecutar(usuario=usuario, id=1)

        repositorio_recordatorios_mock.eliminar.assert_called_once_with(id=1)
