from unittest.mock import MagicMock

import pytest

from app.aplicacion.prospecto.use_cases.registrar_prospecto import RegistrarProspectoUseCase
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_ya_existe import RecursoYaExisteException
from app.dominio.linea_negocio.repositorio_lineas_negocio import RepositorioLineasNegocio
from app.dominio.prospecto.prospecto_empresa.prospecto_empresa import ProspectoEmpresa
from app.dominio.prospecto.repositorio_prospectos import RepositorioProspectos
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.linea_negocio_factory import crear_linea_negocio_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_prospectos_mock():
    mock = MagicMock(spec=RepositorioProspectos)
    mock.buscar_prospecto_por_nombre.return_value = None
    mock.buscar_prospecto_por_rut.return_value = None
    mock.registrar_prospecto_empresa.return_value = 7
    return mock


@pytest.fixture
def repositorio_usuarios_mock():
    mock = MagicMock(spec=RepositorioUsuarios)
    mock.buscar.return_value = crear_usuario_mock(rut='12345678-9')
    return mock


@pytest.fixture
def repositorio_lineas_negocio_mock():
    mock = MagicMock(spec=RepositorioLineasNegocio)
    mock.buscar_por_codigo.return_value = crear_linea_negocio_mock(
        id=12, nombre='Líneas Comerciales', codigo='lineas_comerciales'
    )
    return mock


@pytest.fixture
def use_case(repositorio_prospectos_mock, repositorio_usuarios_mock, repositorio_lineas_negocio_mock):
    return RegistrarProspectoUseCase(
        repositorio_prospectos=repositorio_prospectos_mock,
        repositorio_usuarios=repositorio_usuarios_mock,
        repositorio_lineas_negocio=repositorio_lineas_negocio_mock
    )


def _ejecutar(use_case, **kwargs):
    parametros = {
        'rut_usuario': '12345678-9',
        'rut_riesgo': '76543210-1',
        'id_administrador': None,
        'nombre_riesgo': 'Comercial Andina SpA',
        'telefono_contacto': None,
        'correo_contacto': None,
        'direccion': 'Av. Industrial 456',
        'region': 'Metropolitana',
        'comuna': 'Santiago',
        'observaciones': None,
        'codigo_linea_negocio': 'lineas_comerciales',
    }
    parametros.update(kwargs)
    return use_case.ejecutar(**parametros)


@pytest.mark.unit
class TestRegistrarProspectoLineasComerciales:

    def test_registra_el_prospecto_empresa(self, use_case, repositorio_prospectos_mock,
            repositorio_lineas_negocio_mock):
        resultado = _ejecutar(
            use_case,
            nombre_fantasia='Comercial Andina',
            cantidad_trabajadores=25,
            giros_comerciales=['Comercio', 'Minería']
        )

        assert resultado == 7
        repositorio_lineas_negocio_mock.buscar_por_codigo.assert_called_once_with('lineas_comerciales')
        repositorio_prospectos_mock.registrar_prospecto_empresa.assert_called_once()
        prospecto = repositorio_prospectos_mock.registrar_prospecto_empresa.call_args.args[0]
        assert isinstance(prospecto, ProspectoEmpresa)
        assert prospecto.nombre_fantasia == 'Comercial Andina'
        assert prospecto.cantidad_trabajadores == 25
        assert [giro.nombre for giro in prospecto.giros_comerciales] == ['Comercio', 'Minería']
        assert prospecto.linea_negocio.id == 12

    def test_registra_sin_giros(self, use_case, repositorio_prospectos_mock):
        resultado = _ejecutar(use_case, giros_comerciales=[])

        assert resultado == 7
        prospecto = repositorio_prospectos_mock.registrar_prospecto_empresa.call_args.args[0]
        assert prospecto.giros_comerciales == []

    def test_rechaza_giros_repetidos_en_la_solicitud(self, use_case, repositorio_prospectos_mock):
        with pytest.raises(RecursoYaExisteException):
            _ejecutar(use_case, giros_comerciales=['Comercio', 'comercio'])

        repositorio_prospectos_mock.registrar_prospecto_empresa.assert_not_called()

    def test_linea_de_negocio_inexistente_no_registra(self, use_case,
            repositorio_prospectos_mock, repositorio_lineas_negocio_mock):
        repositorio_lineas_negocio_mock.buscar_por_codigo.return_value = None

        with pytest.raises(DatoInvalidoException):
            _ejecutar(use_case)

        repositorio_prospectos_mock.registrar_prospecto_empresa.assert_not_called()

    def test_nombre_ya_registrado_no_registra(self, use_case, repositorio_prospectos_mock):
        repositorio_prospectos_mock.buscar_prospecto_por_nombre.return_value = crear_prospecto_existente()

        with pytest.raises(RecursoYaExisteException):
            _ejecutar(use_case)

        repositorio_prospectos_mock.registrar_prospecto_empresa.assert_not_called()


@pytest.mark.unit
class TestRegistrarProspectoOtrasLineas:

    def test_lineas_personales_usa_el_prospecto_base(self, use_case, repositorio_prospectos_mock,
            repositorio_lineas_negocio_mock):
        repositorio_lineas_negocio_mock.buscar_por_codigo.return_value = crear_linea_negocio_mock(
            id=11, nombre='Líneas Personales', codigo='lineas_personales'
        )
        repositorio_prospectos_mock.registrar_prospecto.return_value = 8

        resultado = _ejecutar(use_case, codigo_linea_negocio='lineas_personales')

        assert resultado == 8
        repositorio_prospectos_mock.registrar_prospecto.assert_called_once()
        repositorio_prospectos_mock.registrar_prospecto_empresa.assert_not_called()

    def test_condominios_usa_el_prospecto_condominio(self, use_case, repositorio_prospectos_mock,
            repositorio_lineas_negocio_mock):
        repositorio_lineas_negocio_mock.buscar_por_codigo.return_value = crear_linea_negocio_mock(
            id=10, nombre='Condominio', codigo='condominios'
        )
        repositorio_prospectos_mock.registrar_prospecto_condominio.return_value = 9

        resultado = _ejecutar(use_case, codigo_linea_negocio='condominios')

        assert resultado == 9
        repositorio_prospectos_mock.registrar_prospecto_condominio.assert_called_once()
        repositorio_prospectos_mock.registrar_prospecto_empresa.assert_not_called()


def crear_prospecto_existente():
    from tests.factories.prospecto_factory import crear_prospecto_mock
    return crear_prospecto_mock()
