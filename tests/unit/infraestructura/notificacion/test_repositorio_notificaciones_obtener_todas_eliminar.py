from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.notificacion.repositorio_notificaciones_postgres import (
    RepositorioNotificacionesPostgres,
)

MODULO = 'app.infraestructura.notificacion.repositorio_notificaciones_postgres'

FILA = {
    'id': 1,
    'rut_usuario': '11111111-1',
    'codigo_tipo': 'SLA_VENCIDO',
    'nivel': 'CRITICO',
    'titulo': 'Oportunidad fuera de plazo',
    'mensaje': 'mensaje',
    'entidad_tipo': 'PROCESO_COMERCIAL',
    'entidad_id': 42,
    'id_prospecto': 7,
    'dedupe_key': 'SLA_VENCIDO:42:CONTACTO_INICIAL:11111111-1',
    'leida': False,
    'fecha_leida': None,
    'created_at': datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc),
    'leible': False,
}


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
class TestObtenerTodas:

    def test_sin_filtros_no_agrega_where(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = [FILA]

        repo = RepositorioNotificacionesPostgres()
        notificaciones = repo.obtener_todas(codigo_estado=None, leidas=None)

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert 'from Notificacion N' in query_str
        assert 'WHERE' not in query_str
        assert params == {}
        assert len(notificaciones) == 1
        assert notificaciones[0].id == 1
        assert notificaciones[0].rut_usuario == '11111111-1'
        assert notificaciones[0].codigo_tipo == 'SLA_VENCIDO'

    def test_filtra_por_estado_usando_position_en_la_dedupe_key(self, mock_conexion):
        """El segmento de estado se busca con position() y no con LIKE: los
        códigos de estado contienen '_' y LIKE los trataría de comodín."""
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = [FILA]

        repo = RepositorioNotificacionesPostgres()
        repo.obtener_todas(codigo_estado='CONTACTO_INICIAL', leidas=None)

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert "position(':' || %(codigo_estado)s || ':' in N.dedupe_key) > 0" in query_str
        assert 'like' not in query_str.lower()
        assert params == {'codigo_estado': 'CONTACTO_INICIAL'}

    def test_filtra_por_leidas(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = [FILA]

        repo = RepositorioNotificacionesPostgres()
        repo.obtener_todas(codigo_estado=None, leidas=False)

        query, params = cursor.execute.call_args.args
        assert 'N.leida = %(leidas)s' in str(query)
        assert params == {'leidas': False}

    def test_filtra_por_estado_y_leidas_a_la_vez(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = []

        repo = RepositorioNotificacionesPostgres()
        notificaciones = repo.obtener_todas(codigo_estado='CONTACTO_INICIAL', leidas=False)

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert "position(':' || %(codigo_estado)s || ':' in N.dedupe_key) > 0" in query_str
        assert 'N.leida = %(leidas)s' in query_str
        assert params == {'codigo_estado': 'CONTACTO_INICIAL', 'leidas': False}
        assert notificaciones == []

    def test_sin_resultados_devuelve_vacio(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = []

        repo = RepositorioNotificacionesPostgres()

        assert repo.obtener_todas(codigo_estado='ESTADO_VACIO', leidas=False) == []


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestEliminar:

    def test_elimina_por_id(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion

        from app.dominio.notificacion.notificacion import Notificacion

        notificacion = Notificacion(
            id=42,
            rut_usuario='11111111-1',
            codigo_tipo='SLA_VENCIDO',
            nivel='CRITICO',
            titulo='t',
            mensaje='m',
            entidad_tipo='PROCESO_COMERCIAL',
            entidad_id=1,
            id_prospecto=7,
            dedupe_key='SLA_VENCIDO:1:CONTACTO_INICIAL:11111111-1',
            leida=False,
            fecha_leida=None,
            created_at=datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc),
            leible=False,
        )

        repo = RepositorioNotificacionesPostgres()
        repo.eliminar(notificacion)

        query, params = cursor.execute.call_args.args
        assert 'delete from Notificacion' in str(query)
        assert 'where id = %(id)s' in str(query)
        assert params == {'id': 42}
