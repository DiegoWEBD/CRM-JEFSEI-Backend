import pytest
from unittest.mock import MagicMock

from app.aplicacion.administrador_condominio.use_cases.actualizar_administrador import (
    ActualizarAdministradorUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.obtener_administrador_por_id import (
    ObtenerAdministradorPorIdUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.registrar_administrador import (
    RegistrarAdministradorUseCase,
)
from app.dominio.administrador_condominio.repositorio_administradores import (
    RepositorioAdministradores,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from tests.factories.administrador_condominio_factory import crear_administrador_mock


@pytest.fixture
def repositorio_mock():
    mock = MagicMock(spec=RepositorioAdministradores)
    mock.buscar.return_value = crear_administrador_mock()
    mock.guardar.return_value = crear_administrador_mock()
    mock.actualizar.return_value = crear_administrador_mock()
    return mock


@pytest.mark.unit
class TestObtenerAdministradorPorIdUseCase:

    def test_retorna_administrador(self, repositorio_mock):
        use_case = ObtenerAdministradorPorIdUseCase(repositorio_mock)

        resultado = use_case.ejecutar(1)

        assert resultado.id == 1

    def test_inexistente_retorna_404(self, repositorio_mock):
        repositorio_mock.buscar.return_value = None
        use_case = ObtenerAdministradorPorIdUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(999)


@pytest.mark.unit
class TestRegistrarAdministradorUseCase:

    def test_registra_solo_datos_basicos(self, repositorio_mock):
        use_case = RegistrarAdministradorUseCase(repositorio_mock)

        use_case.ejecutar(
            nombre_administrador='Nuevo',
            nombre_contacto='Contacto',
            telefono='123',
            correo='a@b.cl',
        )

        registrado = repositorio_mock.guardar.call_args.args[0]
        assert registrado.nombre_administrador == 'Nuevo'
        # La relación de condominios no forma parte de esta operación.
        assert not hasattr(registrado, 'condominios')


@pytest.mark.unit
class TestActualizarAdministradorUseCase:

    def test_inexistente_retorna_404(self, repositorio_mock):
        repositorio_mock.buscar.return_value = None
        use_case = ActualizarAdministradorUseCase(repositorio_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(
                id=999,
                nombre_administrador='Editado',
                nombre_contacto=None,
                telefono=None,
                correo=None,
            )

        repositorio_mock.actualizar.assert_not_called()

    def test_actualiza_solo_datos_basicos(self, repositorio_mock):
        use_case = ActualizarAdministradorUseCase(repositorio_mock)

        use_case.ejecutar(
            id=1,
            nombre_administrador='Editado',
            nombre_contacto='Contacto',
            telefono='123',
            correo='a@b.cl',
        )

        actualizado = repositorio_mock.actualizar.call_args.args[0]
        assert actualizado.id == 1
        assert actualizado.nombre_administrador == 'Editado'
        assert not hasattr(actualizado, 'condominios')
