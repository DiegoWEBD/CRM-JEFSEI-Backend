import pytest
from unittest.mock import MagicMock

from app.aplicacion.recordatorio.use_cases.registrar_recordatorio import RegistrarRecordatorioUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.recordatorio.repositorio_recordatorios import RepositorioRecordatorios
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_recordatorios_mock():
    return MagicMock(spec=RepositorioRecordatorios)


@pytest.fixture
def repositorio_prospectos_mock():
    return MagicMock(spec=RepositorioProspectos)


@pytest.fixture
def repositorio_usuarios_mock():
    return MagicMock(spec=RepositorioUsuarios)


@pytest.fixture
def use_case(repositorio_recordatorios_mock, repositorio_prospectos_mock, repositorio_usuarios_mock):
    return RegistrarRecordatorioUseCase(
        repositorio_recordatorios_mock,
        repositorio_prospectos_mock,
        repositorio_usuarios_mock,
    )


def _ejecutar(use_case, **kwargs):
    parametros = {
        'rut_usuario': '11111111-1',
        'rut_usuario_destino': None,
        'titulo': 'Llamar al cliente',
        'detalle': None,
        'prioridad': 'MEDIA',
        'tipo_gestion': 'LLAMADA',
        'fecha_recordatorio': '2026-12-01T10:00:00',
        'id_prospecto': None,
    }
    parametros.update(kwargs)
    return use_case.ejecutar(**parametros)


@pytest.mark.unit
class TestRegistrarRecordatorioUseCase:

    def test_sin_destino_registra_para_el_propio_usuario(
        self, use_case, repositorio_recordatorios_mock, repositorio_usuarios_mock,
    ):
        _ejecutar(use_case)

        repositorio_recordatorios_mock.registrar.assert_called_once_with(
            rut_usuario='11111111-1',
            titulo='Llamar al cliente',
            detalle=None,
            prioridad='MEDIA',
            tipo_gestion='LLAMADA',
            fecha_recordatorio='2026-12-01T10:00:00',
            id_prospecto=None,
        )
        repositorio_usuarios_mock.buscar.assert_not_called()

    def test_con_destino_y_permiso_global_registra_para_el_destino(
        self, use_case, repositorio_recordatorios_mock, repositorio_usuarios_mock,
    ):
        solicitante = crear_usuario_mock(rut='11111111-1')
        destino = crear_usuario_mock(rut='22222222-2')
        repositorio_usuarios_mock.buscar.side_effect = lambda rut: {
            '11111111-1': solicitante,
            '22222222-2': destino,
        }.get(rut)
        repositorio_usuarios_mock.usuario_tiene_permiso.return_value = True

        _ejecutar(use_case, rut_usuario_destino='22222222-2')

        repositorio_usuarios_mock.usuario_tiene_permiso.assert_called_once_with(
            solicitante, 'CREAR_RECORDATORIO_GLOBAL'
        )
        repositorio_recordatorios_mock.registrar.assert_called_once_with(
            rut_usuario='22222222-2',
            titulo='Llamar al cliente',
            detalle=None,
            prioridad='MEDIA',
            tipo_gestion='LLAMADA',
            fecha_recordatorio='2026-12-01T10:00:00',
            id_prospecto=None,
        )

    def test_con_destino_sin_permiso_global_lanza_no_autorizado(
        self, use_case, repositorio_recordatorios_mock, repositorio_usuarios_mock,
    ):
        solicitante = crear_usuario_mock(rut='11111111-1')
        repositorio_usuarios_mock.buscar.return_value = solicitante
        repositorio_usuarios_mock.usuario_tiene_permiso.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            _ejecutar(use_case, rut_usuario_destino='22222222-2')

        repositorio_recordatorios_mock.registrar.assert_not_called()

    def test_solicitante_no_existe_lanza_no_autorizado(
        self, use_case, repositorio_recordatorios_mock, repositorio_usuarios_mock,
    ):
        repositorio_usuarios_mock.buscar.return_value = None

        with pytest.raises(UsuarioNoAutorizadoException):
            _ejecutar(use_case, rut_usuario_destino='22222222-2')

        repositorio_recordatorios_mock.registrar.assert_not_called()

    def test_destino_no_existe_lanza_recurso_no_encontrado(
        self, use_case, repositorio_recordatorios_mock, repositorio_usuarios_mock,
    ):
        solicitante = crear_usuario_mock(rut='11111111-1')
        repositorio_usuarios_mock.buscar.side_effect = lambda rut: {
            '11111111-1': solicitante,
        }.get(rut)
        repositorio_usuarios_mock.usuario_tiene_permiso.return_value = True

        with pytest.raises(RecursoNoEncontradoException):
            _ejecutar(use_case, rut_usuario_destino='22222222-2')

        repositorio_recordatorios_mock.registrar.assert_not_called()

    def test_sin_permiso_y_destino_inexistente_lanza_primero_no_autorizado(
        self, use_case, repositorio_recordatorios_mock, repositorio_usuarios_mock,
    ):
        solicitante = crear_usuario_mock(rut='11111111-1')
        repositorio_usuarios_mock.buscar.side_effect = lambda rut: {
            '11111111-1': solicitante,
        }.get(rut)
        repositorio_usuarios_mock.usuario_tiene_permiso.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            _ejecutar(use_case, rut_usuario_destino='22222222-2')

        repositorio_recordatorios_mock.registrar.assert_not_called()

    def test_prospecto_no_existe_lanza_recurso_no_encontrado(
        self, use_case, repositorio_recordatorios_mock, repositorio_prospectos_mock,
    ):
        repositorio_prospectos_mock.buscar.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            _ejecutar(use_case, id_prospecto=99)

        repositorio_recordatorios_mock.registrar.assert_not_called()

    def test_con_destino_y_prospecto_valida_destino_antes_que_prospecto(
        self, use_case, repositorio_prospectos_mock, repositorio_usuarios_mock,
    ):
        solicitante = crear_usuario_mock(rut='11111111-1')
        repositorio_usuarios_mock.buscar.return_value = solicitante
        repositorio_usuarios_mock.usuario_tiene_permiso.return_value = False

        with pytest.raises(UsuarioNoAutorizadoException):
            _ejecutar(use_case, rut_usuario_destino='22222222-2', id_prospecto=99)

        repositorio_prospectos_mock.buscar.assert_not_called()

    def test_pasa_los_datos_al_repositorio(
        self, use_case, repositorio_recordatorios_mock,
    ):
        _ejecutar(
            use_case,
            titulo='Cobrar cuota',
            detalle='Cuota de octubre',
            prioridad='ALTA',
            tipo_gestion='COBRANZA',
            fecha_recordatorio='2026-12-05T09:00:00',
            id_prospecto=7,
        )

        repositorio_recordatorios_mock.registrar.assert_called_once_with(
            rut_usuario='11111111-1',
            titulo='Cobrar cuota',
            detalle='Cuota de octubre',
            prioridad='ALTA',
            tipo_gestion='COBRANZA',
            fecha_recordatorio='2026-12-05T09:00:00',
            id_prospecto=7,
        )
