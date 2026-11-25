import pytest
from unittest.mock import MagicMock

from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.aplicacion.usuario.use_cases.actualizar_perfil import (
    ActualizarPerfilUseCase,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.usuario_factory import crear_usuario_mock


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioUsuarios)


@pytest.fixture
def servicio_auditoria_mock():
    return MagicMock(spec=ServicioAuditoria)


@pytest.fixture
def contexto():
    return ContextoPeticion(ip_origen='127.0.0.1', user_agent='pytest', id_peticion='test-1')


@pytest.mark.unit
class TestActualizarPerfilUseCase:

    def test_actualizar_nombre_exitoso(
        self, repositorio_mock, servicio_auditoria_mock, contexto
    ):
        repositorio_mock.buscar.return_value = crear_usuario_mock(nombre='Nombre Viejo')
        repositorio_mock.actualizar_nombre.return_value = True

        uc = ActualizarPerfilUseCase(repositorio_mock, servicio_auditoria_mock)
        resultado = uc.ejecutar(
            rut='12345678-9',
            nombre='Nombre Nuevo',
            contexto=contexto,
        )

        assert resultado is True
        repositorio_mock.actualizar_nombre.assert_called_once_with(
            '12345678-9', 'Nombre Nuevo'
        )
        servicio_auditoria_mock.registrar_accion_negocio.assert_called_once()

    def test_nombre_se_normaliza_con_trim(
        self, repositorio_mock, servicio_auditoria_mock, contexto
    ):
        repositorio_mock.buscar.return_value = crear_usuario_mock()
        repositorio_mock.actualizar_nombre.return_value = True

        uc = ActualizarPerfilUseCase(repositorio_mock, servicio_auditoria_mock)
        uc.ejecutar(
            rut='12345678-9',
            nombre='   Nombre Nuevo   ',
            contexto=contexto,
        )

        repositorio_mock.actualizar_nombre.assert_called_once_with(
            '12345678-9', 'Nombre Nuevo'
        )

    @pytest.mark.parametrize('nombre', ['', '   ', 'A', 'N' * 121])
    def test_nombre_invalido_es_rechazado(
        self, repositorio_mock, servicio_auditoria_mock, contexto, nombre
    ):
        uc = ActualizarPerfilUseCase(repositorio_mock, servicio_auditoria_mock)

        with pytest.raises(DatoInvalidoException):
            uc.ejecutar(rut='12345678-9', nombre=nombre, contexto=contexto)

        repositorio_mock.actualizar_nombre.assert_not_called()
        servicio_auditoria_mock.registrar_accion_negocio.assert_not_called()

    def test_usuario_no_existe(
        self, repositorio_mock, servicio_auditoria_mock, contexto
    ):
        repositorio_mock.buscar.return_value = None

        uc = ActualizarPerfilUseCase(repositorio_mock, servicio_auditoria_mock)

        with pytest.raises(RecursoNoEncontradoException, match='El usuario no existe'):
            uc.ejecutar(rut='99999999-9', nombre='Nombre', contexto=contexto)

        repositorio_mock.actualizar_nombre.assert_not_called()

    def test_usuario_eliminado(
        self, repositorio_mock, servicio_auditoria_mock, contexto
    ):
        repositorio_mock.buscar.return_value = crear_usuario_mock(eliminado=True)

        uc = ActualizarPerfilUseCase(repositorio_mock, servicio_auditoria_mock)

        with pytest.raises(RecursoNoEncontradoException, match='El usuario no existe'):
            uc.ejecutar(rut='12345678-9', nombre='Nombre', contexto=contexto)

        repositorio_mock.actualizar_nombre.assert_not_called()

    def test_actualizacion_fallida_retorna_false_sin_auditar(
        self, repositorio_mock, servicio_auditoria_mock, contexto
    ):
        repositorio_mock.buscar.return_value = crear_usuario_mock()
        repositorio_mock.actualizar_nombre.return_value = False

        uc = ActualizarPerfilUseCase(repositorio_mock, servicio_auditoria_mock)
        resultado = uc.ejecutar(
            rut='12345678-9',
            nombre='Nombre Nuevo',
            contexto=contexto,
        )

        assert resultado is False
        servicio_auditoria_mock.registrar_accion_negocio.assert_not_called()
