from unittest.mock import MagicMock

import pytest

from app.aplicacion.permiso.use_cases.obtener_permisos import ObtenerPermisosUseCase
from app.dominio.permiso.repositorio_permisos import RepositorioPermisos
from tests.factories.usuario_factory import crear_permiso_mock


@pytest.fixture
def repositorio_permisos_mock():
    return MagicMock(spec=RepositorioPermisos)


@pytest.mark.unit
class TestObtenerPermisosUseCase:

    def test_retorna_catalogo_de_permisos(self, repositorio_permisos_mock):
        permisos = [
            crear_permiso_mock(codigo='ADMINISTRAR_ROLES'),
            crear_permiso_mock(codigo='VER_ALERTAS'),
        ]
        repositorio_permisos_mock.obtener_todos.return_value = permisos

        uc = ObtenerPermisosUseCase(repositorio_permisos_mock)
        resultado = uc.ejecutar()

        assert resultado == permisos
        repositorio_permisos_mock.obtener_todos.assert_called_once()
