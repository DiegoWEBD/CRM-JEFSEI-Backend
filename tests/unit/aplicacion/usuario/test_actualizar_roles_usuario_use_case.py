from unittest.mock import MagicMock

import pytest

from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.aplicacion.usuario.use_cases.actualizar_roles_usuario import ActualizarRolesUsuarioUseCase
from app.dominio.exceptions.conflicto_en_accion_exception import ConflictoEnAccionException
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.rol.repositorio_roles import RepositorioRoles
from app.dominio.usuario.repositorio_usuarios import RepositorioUsuarios
from tests.factories.usuario_factory import (
    crear_rol_mock,
    crear_usuario_admin_mock,
    crear_usuario_mock,
)


@pytest.fixture
def repositorio_usuarios_mock():
    return MagicMock(spec=RepositorioUsuarios)


@pytest.fixture
def repositorio_roles_mock():
    return MagicMock(spec=RepositorioRoles)


@pytest.fixture
def servicio_auditoria_mock():
    return MagicMock(spec=ServicioAuditoria)


@pytest.fixture
def contexto():
    return ContextoPeticion(ip_origen='127.0.0.1', user_agent='pytest', id_peticion='test-1')


@pytest.mark.unit
class TestActualizarRolesUsuarioUseCase:

    def test_actualizacion_exitosa(
        self, repositorio_usuarios_mock, repositorio_roles_mock,
        servicio_auditoria_mock, contexto
    ):
        repositorio_usuarios_mock.buscar.return_value = crear_usuario_mock()
        repositorio_roles_mock.obtener_todos.return_value = [
            crear_rol_mock(codigo='GERENTE_GENERAL'),
            crear_rol_mock(codigo='EJECUTIVO_COMERCIAL'),
        ]
        repositorio_usuarios_mock.asignar_roles.return_value = True

        uc = ActualizarRolesUsuarioUseCase(
            repositorio_usuarios_mock, repositorio_roles_mock, servicio_auditoria_mock
        )
        resultado = uc.ejecutar(
            rut='12345678-9',
            codigo_roles=['GERENTE_GENERAL'],
            usuario_ejecutor=crear_usuario_admin_mock(),
            contexto=contexto,
        )

        assert resultado is True
        repositorio_usuarios_mock.asignar_roles.assert_called_once_with(
            '12345678-9', ['GERENTE_GENERAL']
        )
        servicio_auditoria_mock.registrar_accion_negocio.assert_called_once()

    def test_sin_roles_es_conflicto(
        self, repositorio_usuarios_mock, repositorio_roles_mock,
        servicio_auditoria_mock, contexto
    ):
        uc = ActualizarRolesUsuarioUseCase(
            repositorio_usuarios_mock, repositorio_roles_mock, servicio_auditoria_mock
        )

        with pytest.raises(ConflictoEnAccionException, match='Debe asignar al menos un rol'):
            uc.ejecutar(
                rut='12345678-9',
                codigo_roles=[],
                usuario_ejecutor=crear_usuario_admin_mock(),
                contexto=contexto,
            )

    def test_usuario_no_existe(
        self, repositorio_usuarios_mock, repositorio_roles_mock,
        servicio_auditoria_mock, contexto
    ):
        repositorio_usuarios_mock.buscar.return_value = None

        uc = ActualizarRolesUsuarioUseCase(
            repositorio_usuarios_mock, repositorio_roles_mock, servicio_auditoria_mock
        )

        with pytest.raises(RecursoNoEncontradoException, match='El usuario no existe'):
            uc.ejecutar(
                rut='99999999-9',
                codigo_roles=['GERENTE_GENERAL'],
                usuario_ejecutor=crear_usuario_admin_mock(),
                contexto=contexto,
            )

    def test_usuario_eliminado(
        self, repositorio_usuarios_mock, repositorio_roles_mock,
        servicio_auditoria_mock, contexto
    ):
        repositorio_usuarios_mock.buscar.return_value = crear_usuario_mock(eliminado=True)

        uc = ActualizarRolesUsuarioUseCase(
            repositorio_usuarios_mock, repositorio_roles_mock, servicio_auditoria_mock
        )

        with pytest.raises(RecursoNoEncontradoException, match='El usuario no existe'):
            uc.ejecutar(
                rut='12345678-9',
                codigo_roles=['GERENTE_GENERAL'],
                usuario_ejecutor=crear_usuario_admin_mock(),
                contexto=contexto,
            )

    def test_rol_invalido(
        self, repositorio_usuarios_mock, repositorio_roles_mock,
        servicio_auditoria_mock, contexto
    ):
        repositorio_usuarios_mock.buscar.return_value = crear_usuario_mock()
        repositorio_roles_mock.obtener_todos.return_value = [
            crear_rol_mock(codigo='GERENTE_GENERAL'),
        ]

        uc = ActualizarRolesUsuarioUseCase(
            repositorio_usuarios_mock, repositorio_roles_mock, servicio_auditoria_mock
        )

        with pytest.raises(DatoInvalidoException, match='Roles no válidos: FANTASMA'):
            uc.ejecutar(
                rut='12345678-9',
                codigo_roles=['FANTASMA'],
                usuario_ejecutor=crear_usuario_admin_mock(),
                contexto=contexto,
            )

        repositorio_usuarios_mock.asignar_roles.assert_not_called()
