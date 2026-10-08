from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.notificacion.repositorio_notificaciones_postgres import (
    RepositorioNotificacionesPostgres,
)

MODULO = 'app.infraestructura.notificacion.repositorio_notificaciones_postgres'


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
class TestExisteAlertaProceso:

    def test_consulta_por_tipo_proceso_y_rut(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = {'existe': True}

        repo = RepositorioNotificacionesPostgres()
        resultado = repo.existe_alerta_proceso('FECHA_CIERRE_VENCIDA', 42, '11111111-1')

        assert resultado is True
        query, params = cursor.execute.call_args.args
        assert 'exists' in str(query).lower()
        assert 'Notificacion' in str(query)
        assert params == {
            'codigo_tipo': 'FECHA_CIERRE_VENCIDA',
            'id_proceso': 42,
            'rut_usuario': '11111111-1',
        }

    def test_retorna_false_cuando_no_existe(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = {'existe': False}

        repo = RepositorioNotificacionesPostgres()
        resultado = repo.existe_alerta_proceso('CIERRE_ESTIMADO_PROXIMO', 1, '22222222-2')

        assert resultado is False

    def test_retorna_false_si_no_hay_fila(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = None

        repo = RepositorioNotificacionesPostgres()
        resultado = repo.existe_alerta_proceso('CIERRE_ESTIMADO_PROXIMO', 1, '22222222-2')

        assert resultado is False
