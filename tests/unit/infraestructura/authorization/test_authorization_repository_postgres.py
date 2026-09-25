from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.authorization.authorization_repository_postgres import AuthorizationRepositoryPostgres


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
    "app.infraestructura.authorization.authorization_repository_postgres.obtener_conexion"
)
@pytest.mark.unit
class TestUsuarioPuedeActualizarFechaEstimadaCierre:

    def test_propios_y_asignado_retorna_true(self, obtener_conexion_mock):
        permisos = [{"codigo_permiso": "ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS"}]
        prospecto = {"rut_ej_comercial_asignado": "12345678-9"}
        conexion, cursor = _conexion_mock()
        cursor.fetchall.return_value = permisos
        cursor.fetchone.return_value = prospecto
        obtener_conexion_mock.return_value = conexion

        repo = AuthorizationRepositoryPostgres()
        resultado = repo.usuario_puede_actualizar_fecha_estimada_cierre(
            rut_usuario="12345678-9", id_proceso_comercial=1
        )

        assert resultado is True

    def test_solo_permiso_global_retorna_false(self, obtener_conexion_mock):
        permisos = [{"codigo_permiso": "ADMINISTRAR_PROCESOS_COMERCIALES"}]
        conexion, cursor = _conexion_mock()
        cursor.fetchall.return_value = permisos
        obtener_conexion_mock.return_value = conexion

        repo = AuthorizationRepositoryPostgres()
        resultado = repo.usuario_puede_actualizar_fecha_estimada_cierre(
            rut_usuario="12345678-9", id_proceso_comercial=1
        )

        assert resultado is False

    def test_sin_permiso_propios_retorna_false(self, obtener_conexion_mock):
        permisos = [{"codigo_permiso": "OBTENER_PROSPECTOS_TODOS"}]
        conexion, cursor = _conexion_mock()
        cursor.fetchall.return_value = permisos
        obtener_conexion_mock.return_value = conexion

        repo = AuthorizationRepositoryPostgres()
        resultado = repo.usuario_puede_actualizar_fecha_estimada_cierre(
            rut_usuario="12345678-9", id_proceso_comercial=1
        )

        assert resultado is False
        cursor.fetchone.assert_not_called()

    def test_propios_pero_no_asignado_retorna_false(self, obtener_conexion_mock):
        permisos = [{"codigo_permiso": "ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS"}]
        prospecto = {"rut_ej_comercial_asignado": "99999999-9"}
        conexion, cursor = _conexion_mock()
        cursor.fetchall.return_value = permisos
        cursor.fetchone.return_value = prospecto
        obtener_conexion_mock.return_value = conexion

        repo = AuthorizationRepositoryPostgres()
        resultado = repo.usuario_puede_actualizar_fecha_estimada_cierre(
            rut_usuario="12345678-9", id_proceso_comercial=1
        )

        assert resultado is False

    def test_proceso_inexistente_retorna_false(self, obtener_conexion_mock):
        permisos = [{"codigo_permiso": "ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS"}]
        conexion, cursor = _conexion_mock()
        cursor.fetchall.return_value = permisos
        cursor.fetchone.return_value = None
        obtener_conexion_mock.return_value = conexion

        repo = AuthorizationRepositoryPostgres()
        resultado = repo.usuario_puede_actualizar_fecha_estimada_cierre(
            rut_usuario="12345678-9", id_proceso_comercial=999
        )

        assert resultado is False
