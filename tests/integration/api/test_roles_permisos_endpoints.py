from unittest.mock import MagicMock

import pytest

from tests.integration.api.conftest_api import *

from app.aplicacion.permiso.use_cases.obtener_permisos import ObtenerPermisosUseCase
from app.aplicacion.rol.use_cases.asignar_permisos_rol import AsignarPermisosRolUseCase
from app.aplicacion.rol.use_cases.obtener_roles_con_permisos import ObtenerRolesConPermisosUseCase
from app.aplicacion.usuario.use_cases.actualizar_roles_usuario import ActualizarRolesUsuarioUseCase
from app.dominio.exceptions.recurso_no_encontrado import RecursoNoEncontradoException
from app.main import app
from app.presentacion.api.auth.dependencias.get_current_user import get_current_user
from app.presentacion.api.permiso.deps import get_obtener_permisos_use_case
from app.presentacion.api.rol.deps import (
    get_asignar_permisos_rol_use_case,
    get_obtener_roles_con_permisos_use_case,
)
from app.presentacion.api.usuario.deps import get_actualizar_roles_usuario_use_case
from tests.factories.usuario_factory import (
    crear_permiso_mock,
    crear_rol_mock,
    crear_usuario_mock,
)


@pytest.fixture
def uc_obtener_roles_con_permisos():
    uc = MagicMock(spec=ObtenerRolesConPermisosUseCase)
    uc.ejecutar.return_value = [
        crear_rol_mock(
            codigo='GERENTE_GENERAL',
            nombre='Gerente General',
            permisos=[crear_permiso_mock(codigo='ADMINISTRAR_ROLES')]
        )
    ]
    return uc


@pytest.fixture
def uc_obtener_permisos():
    uc = MagicMock(spec=ObtenerPermisosUseCase)
    uc.ejecutar.return_value = [
        crear_permiso_mock(codigo='ADMINISTRAR_ROLES'),
        crear_permiso_mock(codigo='VER_ALERTAS'),
    ]
    return uc


@pytest.fixture
def uc_asignar_permisos_rol():
    uc = MagicMock(spec=AsignarPermisosRolUseCase)
    uc.ejecutar.return_value = True
    return uc


@pytest.fixture
def uc_actualizar_roles_usuario():
    uc = MagicMock(spec=ActualizarRolesUsuarioUseCase)
    uc.ejecutar.return_value = True
    return uc


@pytest.fixture
def client_con_roles(
    client,
    uc_obtener_roles_con_permisos,
    uc_obtener_permisos,
    uc_asignar_permisos_rol,
    uc_actualizar_roles_usuario,
):
    app.dependency_overrides[get_obtener_roles_con_permisos_use_case] = (
        lambda: uc_obtener_roles_con_permisos
    )
    app.dependency_overrides[get_obtener_permisos_use_case] = (
        lambda: uc_obtener_permisos
    )
    app.dependency_overrides[get_asignar_permisos_rol_use_case] = (
        lambda: uc_asignar_permisos_rol
    )
    app.dependency_overrides[get_actualizar_roles_usuario_use_case] = (
        lambda: uc_actualizar_roles_usuario
    )
    return client


@pytest.mark.integration
class TestObtenerRolesConPermisos:

    def test_retorna_roles_con_permisos(self, client_con_roles, uc_obtener_roles_con_permisos):
        response = client_con_roles.get('/roles/con-permisos')

        assert response.status_code == 200
        data = response.json()['data']
        assert data[0]['codigo'] == 'GERENTE_GENERAL'
        assert data[0]['permisos'] == [
            {'codigo': 'ADMINISTRAR_ROLES', 'descripcion': 'Ver usuarios', 'nombre': 'Ver usuarios'}
        ]


@pytest.mark.integration
class TestObtenerPermisos:

    def test_retorna_catalogo(self, client_con_roles):
        response = client_con_roles.get('/permisos/')

        assert response.status_code == 200
        data = response.json()['data']
        assert {p['codigo'] for p in data} == {'ADMINISTRAR_ROLES', 'VER_ALERTAS'}


@pytest.mark.integration
class TestAsignarPermisosRol:

    def test_asignar_permisos_exitoso(self, client_con_roles, uc_asignar_permisos_rol):
        response = client_con_roles.put(
            '/roles/GERENTE_GENERAL/permisos',
            json={'codigos_permiso': ['VER_ALERTAS']},
        )

        assert response.status_code == 200
        assert response.json()['message'] == 'Permisos del rol actualizados correctamente'

        kwargs = uc_asignar_permisos_rol.ejecutar.call_args.kwargs
        assert kwargs['codigo_rol'] == 'GERENTE_GENERAL'
        assert kwargs['codigos_permiso'] == ['VER_ALERTAS']
        assert kwargs['usuario_ejecutor'].rut == '12345678-9'
        assert kwargs['contexto'].ip_origen is not None

    def test_error_del_use_case_retorna_400(self, client_con_roles, uc_asignar_permisos_rol):
        uc_asignar_permisos_rol.ejecutar.return_value = False

        response = client_con_roles.put(
            '/roles/GERENTE_GENERAL/permisos',
            json={'codigos_permiso': []},
        )

        assert response.status_code == 400

    def test_rol_inexistente_retorna_404(self, client_con_roles, uc_asignar_permisos_rol):
        uc_asignar_permisos_rol.ejecutar.side_effect = RecursoNoEncontradoException(
            'El rol no existe'
        )

        response = client_con_roles.put(
            '/roles/INEXISTENTE/permisos',
            json={'codigos_permiso': []},
        )

        assert response.status_code == 404

    def test_sin_permiso_administrar_roles_retorna_403(
        self, client_con_roles, uc_asignar_permisos_rol
    ):
        app.dependency_overrides[get_current_user] = lambda: crear_usuario_mock()

        response = client_con_roles.put(
            '/roles/GERENTE_GENERAL/permisos',
            json={'codigos_permiso': []},
        )

        assert response.status_code == 403
        uc_asignar_permisos_rol.ejecutar.assert_not_called()


@pytest.mark.integration
class TestActualizarRolesUsuario:

    def test_actualizar_roles_exitoso(self, client_con_roles, uc_actualizar_roles_usuario):
        response = client_con_roles.put(
            '/usuarios/12345678-9/roles',
            json={'codigo_roles': ['GERENTE_GENERAL', 'EJECUTIVO_COMERCIAL']},
        )

        assert response.status_code == 200
        assert response.json()['message'] == 'Roles del usuario actualizados correctamente'

        kwargs = uc_actualizar_roles_usuario.ejecutar.call_args.kwargs
        assert kwargs['rut'] == '12345678-9'
        assert kwargs['codigo_roles'] == ['GERENTE_GENERAL', 'EJECUTIVO_COMERCIAL']

    def test_error_del_use_case_retorna_400(
        self, client_con_roles, uc_actualizar_roles_usuario
    ):
        uc_actualizar_roles_usuario.ejecutar.return_value = False

        response = client_con_roles.put(
            '/usuarios/12345678-9/roles',
            json={'codigo_roles': ['GERENTE_GENERAL']},
        )

        assert response.status_code == 400
