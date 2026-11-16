from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.rol.repositorio_roles_postgres import RepositorioRolesPostgres


def _conexion_mock(rows=None, row=None):
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    if rows is not None:
        cursor.fetchall.return_value = rows
    if row is not None:
        cursor.fetchone.return_value = row
    return conexion, cursor


@patch(
    "app.infraestructura.rol.repositorio_roles_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestObtenerPorCodigo:

    def test_rol_existe(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(
            row={"codigo": "GERENTE_GENERAL", "nombre": "Gerente General"}
        )
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioRolesPostgres()
        rol = repo.obtener_por_codigo("GERENTE_GENERAL")

        assert rol is not None
        assert rol.codigo == "GERENTE_GENERAL"
        assert rol.nombre == "Gerente General"

    def test_rol_no_existe(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        cursor.fetchone.return_value = None
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioRolesPostgres()
        rol = repo.obtener_por_codigo("INEXISTENTE")

        assert rol is None


@patch(
    "app.infraestructura.rol.repositorio_roles_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestObtenerConPermisos:

    def test_agrupa_permisos_por_rol(self, obtener_conexion_mock):
        rows = [
            {
                "codigo": "GERENTE_GENERAL",
                "nombre": "Gerente General",
                "permiso_codigo": "ADMINISTRAR_ROLES",
                "permiso_descripcion": "Administrar roles",
                "permiso_nombre": "Administrar roles",
            },
            {
                "codigo": "GERENTE_GENERAL",
                "nombre": "Gerente General",
                "permiso_codigo": "VER_ALERTAS",
                "permiso_descripcion": "Ver alertas",
                "permiso_nombre": "Ver alertas",
            },
            {
                "codigo": "EJECUTIVO_COMERCIAL",
                "nombre": "Ejecutivo Comercial",
                "permiso_codigo": None,
                "permiso_descripcion": None,
                "permiso_nombre": None,
            },
        ]
        conexion, cursor = _conexion_mock(rows=rows)
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioRolesPostgres()
        roles = repo.obtener_con_permisos()

        assert len(roles) == 2
        gerente = next(r for r in roles if r.codigo == "GERENTE_GENERAL")
        assert [p.codigo for p in gerente.permisos] == [
            "ADMINISTRAR_ROLES", "VER_ALERTAS"
        ]
        ejecutivo = next(r for r in roles if r.codigo == "EJECUTIVO_COMERCIAL")
        assert ejecutivo.permisos == []


@patch(
    "app.infraestructura.rol.repositorio_roles_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestAsignarPermisos:

    def test_reemplaza_los_permisos_del_rol(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioRolesPostgres()
        resultado = repo.asignar_permisos(
            "GERENTE_GENERAL", ["VER_ALERTAS", "OBTENER_ROLES"]
        )

        assert resultado is True
        assert cursor.execute.call_count == 3
        delete_params = cursor.execute.call_args_list[0].args[1]
        assert delete_params == {"codigo_rol": "GERENTE_GENERAL"}

    def test_lista_vacia_solo_elimina(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioRolesPostgres()
        resultado = repo.asignar_permisos("GERENTE_GENERAL", [])

        assert resultado is True
        assert cursor.execute.call_count == 1
