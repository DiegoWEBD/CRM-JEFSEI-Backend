from unittest.mock import MagicMock

import pytest

from app.aplicacion.auditoria.dtos.contexto_peticion import ContextoPeticion
from app.aplicacion.auditoria.servicio_auditoria import ServicioAuditoria
from app.aplicacion.rol.use_cases.asignar_permisos_rol import AsignarPermisosRolUseCase
from app.aplicacion.rol.use_cases.obtener_roles_con_permisos import ObtenerRolesConPermisosUseCase
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.dominio.permiso.repositorio_permisos import RepositorioPermisos
from app.dominio.rol.repositorio_roles import RepositorioRoles
from tests.factories.usuario_factory import (
    crear_permiso_mock,
    crear_rol_mock,
    crear_usuario_admin_mock,
)


@pytest.fixture
def repositorio_roles_mock():
    return MagicMock(spec=RepositorioRoles)


@pytest.fixture
def repositorio_permisos_mock():
    return MagicMock(spec=RepositorioPermisos)


@pytest.fixture
def servicio_auditoria_mock():
    return MagicMock(spec=ServicioAuditoria)


@pytest.fixture
def contexto():
    return ContextoPeticion(ip_origen='127.0.0.1', user_agent='pytest', id_peticion='test-1')


@pytest.mark.unit
class TestObtenerRolesConPermisosUseCase:

    def test_retorna_roles_con_sus_permisos(self, repositorio_roles_mock):
        roles = [
            crear_rol_mock(
                codigo='GERENTE_GENERAL',
                nombre='Gerente General',
                permisos=[crear_permiso_mock(codigo='ADMINISTRAR_ROLES')]
            )
        ]
        repositorio_roles_mock.obtener_con_permisos.return_value = roles

        uc = ObtenerRolesConPermisosUseCase(repositorio_roles_mock)
        resultado = uc.ejecutar()

        assert resultado == roles
        repositorio_roles_mock.obtener_con_permisos.assert_called_once()


@pytest.mark.unit
class TestAsignarPermisosRolUseCase:

    def test_asignar_permisos_exitoso(
        self, repositorio_roles_mock, repositorio_permisos_mock,
        servicio_auditoria_mock, contexto
    ):
        repositorio_roles_mock.obtener_por_codigo.return_value = crear_rol_mock()
        repositorio_permisos_mock.obtener_por_codigos.return_value = [
            crear_permiso_mock(codigo='VER_ALERTAS'),
            crear_permiso_mock(codigo='OBTENER_ROLES'),
        ]
        repositorio_roles_mock.asignar_permisos.return_value = True
        usuario = crear_usuario_admin_mock()

        uc = AsignarPermisosRolUseCase(
            repositorio_roles_mock, repositorio_permisos_mock, servicio_auditoria_mock
        )
        resultado = uc.ejecutar(
            codigo_rol='GERENTE',
            codigos_permiso=['VER_ALERTAS', 'OBTENER_ROLES'],
            usuario_ejecutor=usuario,
            contexto=contexto,
        )

        assert resultado is True
        repositorio_roles_mock.asignar_permisos.assert_called_once_with(
            'GERENTE', ['VER_ALERTAS', 'OBTENER_ROLES']
        )
        servicio_auditoria_mock.registrar_accion_negocio.assert_called_once()

    def test_rol_no_existe(self, repositorio_roles_mock, repositorio_permisos_mock,
                           servicio_auditoria_mock, contexto):
        repositorio_roles_mock.obtener_por_codigo.return_value = None

        uc = AsignarPermisosRolUseCase(
            repositorio_roles_mock, repositorio_permisos_mock, servicio_auditoria_mock
        )

        with pytest.raises(RecursoNoEncontradoException, match='El rol no existe'):
            uc.ejecutar(
                codigo_rol='INEXISTENTE',
                codigos_permiso=['VER_ALERTAS'],
                usuario_ejecutor=crear_usuario_admin_mock(),
                contexto=contexto,
            )

        repositorio_roles_mock.asignar_permisos.assert_not_called()

    def test_permiso_invalido(self, repositorio_roles_mock, repositorio_permisos_mock,
                              servicio_auditoria_mock, contexto):
        repositorio_roles_mock.obtener_por_codigo.return_value = crear_rol_mock()
        repositorio_permisos_mock.obtener_por_codigos.return_value = []

        uc = AsignarPermisosRolUseCase(
            repositorio_roles_mock, repositorio_permisos_mock, servicio_auditoria_mock
        )

        with pytest.raises(DatoInvalidoException, match='Permisos no válidos: FANTASMA'):
            uc.ejecutar(
                codigo_rol='GERENTE',
                codigos_permiso=['FANTASMA'],
                usuario_ejecutor=crear_usuario_admin_mock(),
                contexto=contexto,
            )

        repositorio_roles_mock.asignar_permisos.assert_not_called()

    def test_deduplica_codigos_repetidos(
        self, repositorio_roles_mock, repositorio_permisos_mock,
        servicio_auditoria_mock, contexto
    ):
        repositorio_roles_mock.obtener_por_codigo.return_value = crear_rol_mock()
        repositorio_permisos_mock.obtener_por_codigos.return_value = [
            crear_permiso_mock(codigo='VER_ALERTAS'),
        ]
        repositorio_roles_mock.asignar_permisos.return_value = True

        uc = AsignarPermisosRolUseCase(
            repositorio_roles_mock, repositorio_permisos_mock, servicio_auditoria_mock
        )
        uc.ejecutar(
            codigo_rol='GERENTE',
            codigos_permiso=['VER_ALERTAS', 'VER_ALERTAS'],
            usuario_ejecutor=crear_usuario_admin_mock(),
            contexto=contexto,
        )

        repositorio_roles_mock.asignar_permisos.assert_called_once_with(
            'GERENTE', ['VER_ALERTAS']
        )
