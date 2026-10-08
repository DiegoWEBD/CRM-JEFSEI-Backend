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
    'codigo_tipo': 'FECHA_CIERRE_VENCIDA',
    'nivel': 'CRITICO',
    'titulo': 'Fecha de cierre vencida',
    'mensaje': 'mensaje',
    'entidad_tipo': 'PROCESO_COMERCIAL',
    'entidad_id': 42,
    'id_prospecto': 7,
    'dedupe_key': 'FECHA_CIERRE_VENCIDA:42:11111111-1:2026-10-07T12:00:00+00:00',
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


def _notificacion_desde_fila(**cambios):
    from app.dominio.notificacion.notificacion import Notificacion

    fila = {**FILA, **cambios}
    return Notificacion(
        id=fila['id'],
        rut_usuario=fila['rut_usuario'],
        codigo_tipo=fila['codigo_tipo'],
        nivel=fila['nivel'],
        titulo=fila['titulo'],
        mensaje=fila['mensaje'],
        entidad_tipo=fila['entidad_tipo'],
        entidad_id=fila['entidad_id'],
        id_prospecto=fila['id_prospecto'],
        dedupe_key=fila['dedupe_key'],
        leida=fila['leida'],
        fecha_leida=fila['fecha_leida'],
        created_at=fila['created_at'],
        leible=fila['leible'],
    )


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestBuscarNotificacionesProcesoComercial:

    def test_filtra_por_proceso_comercial(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = [FILA]

        repo = RepositorioNotificacionesPostgres()
        notificaciones = repo.buscar_notificaciones_proceso_comercial(42)

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert "N.entidad_tipo = 'PROCESO_COMERCIAL'" in query_str
        assert 'N.entidad_id = %(id_proceso_comercial)s' in query_str
        assert params == {'id_proceso_comercial': 42}
        assert len(notificaciones) == 1
        assert notificaciones[0].id == 1
        assert notificaciones[0].rut_usuario == '11111111-1'
        assert notificaciones[0].codigo_tipo == 'FECHA_CIERRE_VENCIDA'

    def test_sin_notificaciones_devuelve_vacio(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = []

        repo = RepositorioNotificacionesPostgres()

        assert repo.buscar_notificaciones_proceso_comercial(42) == []


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestActualizarNotificacion:

    def test_actualiza_todos_los_campos_editables(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        notificacion = _notificacion_desde_fila(leida=True)

        repo = RepositorioNotificacionesPostgres()
        repo.actualizar(notificacion)

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert 'update Notificacion' in query_str
        for campo in ('rut_usuario', 'codigo_tipo', 'nivel', 'titulo', 'mensaje',
                      'entidad_tipo', 'entidad_id', 'id_prospecto', 'dedupe_key',
                      'leida', 'fecha_leida', 'leible'):
            assert f'{campo} = %({campo})s' in query_str, f'falta {campo} en el update'
        assert 'created_at' not in query_str
        assert 'where id = %(id)s' in query_str
        assert params['id'] == 1
        assert params['leida'] is True
        assert params['rut_usuario'] == '11111111-1'
        assert params['dedupe_key'] == FILA['dedupe_key']

    def test_actualiza_tambien_los_nulos(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        notificacion = _notificacion_desde_fila(fecha_leida=None, entidad_id=None)

        repo = RepositorioNotificacionesPostgres()
        repo.actualizar(notificacion)

        params = cursor.execute.call_args.args[1]
        assert params['fecha_leida'] is None
        assert params['entidad_id'] is None
