from unittest.mock import MagicMock, patch

import pytest

import app.infraestructura.estudio_comercial_condominio.repositorio_estudios_comerciales_postgres as modulo_repo
from app.infraestructura.estudio_comercial_condominio.repositorio_estudios_comerciales_postgres import (
    RepositorioEstudiosComercialesPostgres,
)

MODULO = (
    'app.infraestructura.estudio_comercial_condominio'
    '.repositorio_estudios_comerciales_postgres'
)


def _conexion_mock():
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    return conexion, cursor


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestInsertarEstudioPuro:

    def test_devuelve_tupla_estudio_y_proceso(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.side_effect = [
            {'id': 5},
            {'id_proceso_comercial': 9},
        ]

        repo = RepositorioEstudiosComercialesPostgres()
        resultado = repo.insertar(
            id_solicitud=3, nombre_archivo='estudio.pdf', rut_usuario='99999999-9'
        )

        assert resultado == (5, 9)

    def test_no_toca_notificaciones_ni_publica(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.side_effect = [
            {'id': 5},
            {'id_proceso_comercial': 9},
        ]

        repo = RepositorioEstudiosComercialesPostgres()
        repo.insertar(id_solicitud=3, nombre_archivo='estudio.pdf', rut_usuario='99999999-9')

        for call in cursor.execute.call_args_list:
            assert 'Notificacion' not in str(call.args[0])

    def test_el_modulo_no_expone_hub_ni_funciones_de_alertas(self, mock_conexion):
        assert not hasattr(modulo_repo, 'hub')
        assert not hasattr(modulo_repo, 'marcar_alertas_sla_leidas')
