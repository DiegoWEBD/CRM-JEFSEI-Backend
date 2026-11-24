import pytest
from unittest.mock import MagicMock

from app.aplicacion.administrador_condominio.servicios.consulta_administradores_service import (
    ConsultaAdministradoresService,
)
from app.aplicacion.administrador_condominio.use_cases.actualizar_administrador import (
    ActualizarAdministradorUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.obtener_administrador_por_id import (
    ObtenerAdministradorPorIdUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.obtener_administradores import (
    ObtenerAdministradoresUseCase,
)
from app.aplicacion.administrador_condominio.use_cases.registrar_administrador import (
    RegistrarAdministradorUseCase,
)
from app.aplicacion.authorization.authorization_service import AuthorizationService
from app.dominio.administrador_condominio.repositorio_administradores import (
    RepositorioAdministradores,
)
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.exceptions.usuario_no_autorizado import UsuarioNoAutorizadoException
from tests.factories.administrador_condominio_factory import crear_administrador_mock
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_mock():
    mock = MagicMock(spec=RepositorioAdministradores)
    mock.buscar.return_value = crear_administrador_mock()
    mock.guardar.return_value = crear_administrador_mock()
    mock.actualizar.return_value = crear_administrador_mock()
    return mock


@pytest.fixture
def authorization_service_mock():
    return MagicMock(spec=AuthorizationService)


@pytest.fixture
def usuario():
    return crear_usuario_mock(rut='11111111-1')


@pytest.mark.unit
class TestObtenerAdministradorPorIdUseCase:

    def test_sin_permiso_retorna_403(self, repositorio_mock, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_ver_administradores.return_value = False
        use_case = ObtenerAdministradorPorIdUseCase(repositorio_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario, id=1)

        repositorio_mock.buscar.assert_not_called()

    def test_con_permiso_retorna_administrador(self, repositorio_mock, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_ver_administradores.return_value = True
        use_case = ObtenerAdministradorPorIdUseCase(repositorio_mock, authorization_service_mock)

        resultado = use_case.ejecutar(usuario=usuario, id=1)

        assert resultado.id == 1

    def test_inexistente_retorna_404(self, repositorio_mock, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_ver_administradores.return_value = True
        repositorio_mock.buscar.return_value = None
        use_case = ObtenerAdministradorPorIdUseCase(repositorio_mock, authorization_service_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(usuario=usuario, id=999)


@pytest.mark.unit
class TestObtenerAdministradoresUseCase:

    def test_sin_permiso_retorna_403(self, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_ver_administradores.return_value = False
        consulta_mock = MagicMock(spec=ConsultaAdministradoresService)
        use_case = ObtenerAdministradoresUseCase(consulta_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(usuario=usuario)

        consulta_mock.obtener_todos.assert_not_called()

    def test_con_permiso_lista(self, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_ver_administradores.return_value = True
        consulta_mock = MagicMock(spec=ConsultaAdministradoresService)
        consulta_mock.obtener_todos.return_value = {'data': [], 'total': 0}
        use_case = ObtenerAdministradoresUseCase(consulta_mock, authorization_service_mock)

        resultado = use_case.ejecutar(usuario=usuario, texto_busqueda='abc', pagina=2, tamano_pagina=10)

        assert resultado == {'data': [], 'total': 0}
        consulta_mock.obtener_todos.assert_called_once_with(
            texto_busqueda='abc', pagina=2, tamano_pagina=10
        )


@pytest.mark.unit
class TestRegistrarAdministradorUseCase:

    def test_sin_permiso_retorna_403(self, repositorio_mock, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_administrar_administradores.return_value = False
        use_case = RegistrarAdministradorUseCase(repositorio_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(
                usuario=usuario,
                nombre_administrador='Nuevo',
                nombre_contacto=None,
                telefono=None,
                correo=None,
            )

        repositorio_mock.guardar.assert_not_called()

    def test_con_permiso_registra_solo_datos_basicos(self, repositorio_mock, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_administrar_administradores.return_value = True
        use_case = RegistrarAdministradorUseCase(repositorio_mock, authorization_service_mock)

        use_case.ejecutar(
            usuario=usuario,
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

    def test_sin_permiso_retorna_403_sin_operar(self, repositorio_mock, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_administrar_administradores.return_value = False
        use_case = ActualizarAdministradorUseCase(repositorio_mock, authorization_service_mock)

        with pytest.raises(UsuarioNoAutorizadoException):
            use_case.ejecutar(
                usuario=usuario,
                id=1,
                nombre_administrador='Editado',
                nombre_contacto=None,
                telefono=None,
                correo=None,
            )

        repositorio_mock.buscar.assert_not_called()
        repositorio_mock.actualizar.assert_not_called()

    def test_inexistente_retorna_404(self, repositorio_mock, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_administrar_administradores.return_value = True
        repositorio_mock.buscar.return_value = None
        use_case = ActualizarAdministradorUseCase(repositorio_mock, authorization_service_mock)

        with pytest.raises(RecursoNoEncontradoException):
            use_case.ejecutar(
                usuario=usuario,
                id=999,
                nombre_administrador='Editado',
                nombre_contacto=None,
                telefono=None,
                correo=None,
            )

    def test_con_permiso_actualiza_solo_datos_basicos(self, repositorio_mock, authorization_service_mock, usuario):
        authorization_service_mock.usuario_puede_administrar_administradores.return_value = True
        use_case = ActualizarAdministradorUseCase(repositorio_mock, authorization_service_mock)

        use_case.ejecutar(
            usuario=usuario,
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
