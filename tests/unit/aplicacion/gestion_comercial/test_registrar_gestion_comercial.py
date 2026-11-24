import pytest
from unittest.mock import MagicMock

from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.aplicacion.gestion_comercial.use_cases.registrar_gestion_comercial import RegistrarGestionComercialUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.gestion_comercial.repositorio_gestiones_comerciales import RepositorioGestionesComerciales
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from tests.factories.gestion_comercial_factory import crear_gestion_comercial_mock
from tests.factories.prospecto_factory import crear_prospecto_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_mock():
    mock = MagicMock(spec=RepositorioGestionesComerciales)
    mock.registrar.return_value = crear_gestion_comercial_mock()
    return mock


@pytest.fixture
def repositorio_recordatorios_mock():
    return MagicMock(spec=RepositorioRecordatorios)


@pytest.fixture
def repositorio_prospectos_mock():
    mock = MagicMock(spec=RepositorioProspectos)
    mock.buscar.return_value = crear_prospecto_mock(id=7)
    return mock


@pytest.fixture
def authorization_service_mock():
    return MagicMock(spec=AuthorizationService)


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='11111111-1')


@pytest.fixture
def use_case(repositorio_mock, repositorio_recordatorios_mock, repositorio_prospectos_mock, authorization_service_mock):
    return RegistrarGestionComercialUseCase(
        repositorio_mock,
        repositorio_recordatorios_mock,
        repositorio_prospectos_mock,
        authorization_service_mock,
    )


def _ejecutar(use_case, usuario, **kwargs):
    parametros = {
        'usuario': usuario,
        'tipo': 'correo',
        'id_prospecto': 7,
        'titulo': 'Contacto inicial',
        'estado_contacto': None,
        'observacion': None,
        'fecha_gestion': '2026-11-20T10:00:00',
    }
    parametros.update(kwargs)
    return use_case.ejecutar(**parametros)


@pytest.mark.unit
class TestRegistrarGestionComercialUseCase:

    def test_prospecto_inexistente_retorna_404(
        self, use_case, repositorio_mock, repositorio_prospectos_mock, usuario,
    ):
        repositorio_prospectos_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            _ejecutar(use_case, usuario)

        repositorio_mock.registrar.assert_not_called()

    def test_sin_autorizacion_retorna_403(
        self, use_case, repositorio_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_registrar_gestion_comercial.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            _ejecutar(use_case, usuario)

        authorization_service_mock.usuario_puede_registrar_gestion_comercial.assert_called_once_with(usuario, 7)
        repositorio_mock.registrar.assert_not_called()

    def test_con_autorizacion_registra_a_nombre_del_usuario(
        self, use_case, repositorio_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_registrar_gestion_comercial.return_value = True

        _ejecutar(use_case, usuario)

        assert repositorio_mock.registrar.call_args.kwargs['rut_usuario'] == '11111111-1'

    def test_llamada_con_estado_de_seguimiento_agenda_recordatorios(
        self, use_case, repositorio_mock, repositorio_recordatorios_mock, authorization_service_mock, usuario,
    ):
        authorization_service_mock.usuario_puede_registrar_gestion_comercial.return_value = True

        _ejecutar(use_case, usuario, tipo='llamada', estado_contacto='no_contesta')

        # SCHEDULE_RULES['no_contesta'] = 11 recordatorios
        assert repositorio_recordatorios_mock.registrar.call_count == 11
