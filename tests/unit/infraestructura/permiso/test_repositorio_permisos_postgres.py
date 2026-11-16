from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.permiso.repositorio_permisos_postgres import RepositorioPermisosPostgres


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
    "app.infraestructura.permiso.repositorio_permisos_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestRepositorioPermisosPostgres:

    def test_obtener_todos(self, obtener_conexion_mock):
        rows = [
            {"codigo": "ADMINISTRAR_ROLES", "descripcion": "Administrar roles"},
            {"codigo": "VER_ALERTAS", "descripcion": "Ver alertas"},
        ]
        conexion, cursor = _conexion_mock(rows=rows)
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioPermisosPostgres()
        permisos = repo.obtener_todos()

        assert [p.codigo for p in permisos] == ["ADMINISTRAR_ROLES", "VER_ALERTAS"]

    def test_obtener_por_codigos(self, obtener_conexion_mock):
        rows = [{"codigo": "VER_ALERTAS", "descripcion": "Ver alertas"}]
        conexion, cursor = _conexion_mock(rows=rows)
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioPermisosPostgres()
        permisos = repo.obtener_por_codigos(["VER_ALERTAS", "FANTASMA"])

        assert [p.codigo for p in permisos] == ["VER_ALERTAS"]
        params = cursor.execute.call_args.args[1]
        assert params == {"codigos": ["VER_ALERTAS", "FANTASMA"]}

    def test_obtener_por_codigos_vacio_no_consulta(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioPermisosPostgres()
        permisos = repo.obtener_por_codigos([])

        assert permisos == []
        cursor.execute.assert_not_called()
