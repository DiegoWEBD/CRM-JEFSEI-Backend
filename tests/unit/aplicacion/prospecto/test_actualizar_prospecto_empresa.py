from unittest.mock import MagicMock

import pytest

from app.aplicacion.prospecto.use_cases.actualizar_prospecto_empresa import ActualizarProspectoEmpresaUseCase
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from tests.factories.prospecto_factory import crear_prospecto_empresa_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_prospectos_mock():
    mock = MagicMock(spec=RepositorioProspectos)
    mock.buscar_prospecto_empresa.return_value = crear_prospecto_empresa_mock(
        id=1,
        ejecutivo_comercial_asignado=crear_usuario_mock(rut='12345678-9'),
        giros_comerciales=['Comercio'],
    )
    mock.buscar_prospecto_por_nombre.return_value = None
    mock.buscar_prospecto_por_rut.return_value = None
    mock.existe_giro_comercial_por_nombre.return_value = False
    return mock


@pytest.fixture
def use_case(repositorio_prospectos_mock):
    return ActualizarProspectoEmpresaUseCase(repositorio_prospectos_mock)


def _ejecutar(use_case, **kwargs):
    parametros = {
        'id': 1,
        'rut_usuario': '12345678-9',
        'rut_riesgo': '76543210-1',
        'nombre_riesgo': 'Comercial Andina SpA',
        'telefono_contacto': None,
        'correo_contacto': None,
        'direccion': 'Av. Industrial 456',
        'region': 'Metropolitana',
        'comuna': 'Santiago',
        'observaciones': None,
        'nombre_fantasia': 'Comercial Andina',
        'cantidad_trabajadores': 30,
        'giros_comerciales': ['Comercio'],
    }
    parametros.update(kwargs)
    return use_case.ejecutar(**parametros)


@pytest.mark.unit
class TestActualizarProspectoEmpresa:

    def test_actualiza_la_ficha_de_empresa(self, use_case, repositorio_prospectos_mock):
        _ejecutar(
            use_case,
            nombre_fantasia='Comercial Andina Sur',
            cantidad_trabajadores=40,
            giros_comerciales=['Comercio', 'Minería'],
        )

        repositorio_prospectos_mock.actualizar_prospecto_empresa.assert_called_once()
        prospecto = repositorio_prospectos_mock.actualizar_prospecto_empresa.call_args.args[0]
        assert prospecto.nombre_fantasia == 'Comercial Andina Sur'
        assert prospecto.cantidad_trabajadores == 40
        assert [giro.nombre for giro in prospecto.giros_comerciales] == ['Comercio', 'Minería']

    def test_conserva_los_giros_ya_registrados(self, use_case, repositorio_prospectos_mock):
        _ejecutar(use_case, giros_comerciales=['Comercio'])

        repositorio_prospectos_mock.existe_giro_comercial_por_nombre.assert_not_called()
        repositorio_prospectos_mock.actualizar_prospecto_empresa.assert_called_once()

    def test_rechaza_giro_con_nombre_ya_registrado(self, use_case, repositorio_prospectos_mock):
        repositorio_prospectos_mock.existe_giro_comercial_por_nombre.return_value = True

        with pytest.raises(RecursoYaExisteException):
            _ejecutar(use_case, giros_comerciales=['Comercio', 'comercio al por mayor'])

        repositorio_prospectos_mock.existe_giro_comercial_por_nombre.assert_called_once_with(1, 'comercio al por mayor')
        repositorio_prospectos_mock.actualizar_prospecto_empresa.assert_not_called()

    def test_rechaza_giros_repetidos_en_la_solicitud(self, use_case, repositorio_prospectos_mock):
        with pytest.raises(RecursoYaExisteException):
            _ejecutar(use_case, giros_comerciales=['Molienda', 'moliénda'])

        repositorio_prospectos_mock.actualizar_prospecto_empresa.assert_not_called()

    def test_rechaza_giro_con_nombre_vacio(self, use_case, repositorio_prospectos_mock):
        with pytest.raises(ConflictoEnAccionException):
            _ejecutar(use_case, giros_comerciales=['  '])

        repositorio_prospectos_mock.actualizar_prospecto_empresa.assert_not_called()

    def test_prospecto_inexistente_no_actualiza(self, use_case, repositorio_prospectos_mock):
        repositorio_prospectos_mock.buscar_prospecto_empresa.return_value = None

        with pytest.raises(RecursoNoEncontradoException):
            _ejecutar(use_case)

        repositorio_prospectos_mock.actualizar_prospecto_empresa.assert_not_called()

    def test_solo_el_ejecutivo_comercial_asignado_actualiza(self, use_case, repositorio_prospectos_mock):
        repositorio_prospectos_mock.buscar_prospecto_empresa.return_value = crear_prospecto_empresa_mock(
            id=1,
            ejecutivo_comercial_asignado=crear_usuario_mock(rut='99999999-9'),
        )

        with pytest.raises(UsuarioNoAutorizadoException):
            _ejecutar(use_case)

        repositorio_prospectos_mock.actualizar_prospecto_empresa.assert_not_called()
