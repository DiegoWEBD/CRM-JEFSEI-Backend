from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.notificacion.repositorio_notificaciones_postgres import (
    RepositorioNotificacionesPostgres,
)

MODULO = 'app.infraestructura.notificacion.repositorio_notificaciones_postgres'

FILA_POLIZA = {
    'numero_poliza': 'POL-001',
    'fin_vigencia': datetime(2026, 12, 31, 0, 0, 0, tzinfo=timezone.utc),
    'id_prospecto': 7,
    'nombre_cliente': 'Cliente Test',
    'rut_ej_renovacion_asignado': '11111111-1',
    'rut_as_renovacion_asignado': None,
    'tiene_proceso_renovacion': False,
}

FILA_NOTIFICACION = {
    'id': 1,
    'rut_usuario': '11111111-1',
    'codigo_tipo': 'RENOVACION_GESTION_PENDIENTE',
    'nivel': 'AVISO',
    'titulo': 'Gestionar renovación',
    'mensaje': 'mensaje',
    'entidad_tipo': None,
    'entidad_id': None,
    'id_prospecto': 7,
    'numero_poliza': 'POL-001',
    'dedupe_key': 'RENOVACION_GESTION_PENDIENTE:POL-001:2026-12-31T00:00:00+00:00:11111111-1',
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
class TestObtenerPolizasAlertablesRenovacion:

    def test_trae_polizas_en_horizonte_con_responsables_y_proceso(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = [FILA_POLIZA]

        repo = RepositorioNotificacionesPostgres()
        polizas = repo.obtener_polizas_alertables_renovacion()

        query, *resto = cursor.execute.call_args.args
        query_str = str(query)
        assert 'P.cancelada = false' in query_str
        assert 'P.fin_vigencia is not null' in query_str
        assert "(P.fin_vigencia - interval '2 months') <= now()" in query_str
        assert 'ProcesoComercialRenovacion' in query_str
        assert 'C.rut_ej_renovacion_asignado' in query_str
        assert 'C.rut_as_renovacion_asignado' in query_str
        assert resto == []
        assert len(polizas) == 1
        assert polizas[0].numero_poliza == 'POL-001'
        assert polizas[0].id_prospecto == 7
        assert polizas[0].rut_ej_renovacion == '11111111-1'
        assert polizas[0].rut_as_renovacion is None
        assert polizas[0].tiene_proceso_renovacion is False

    def test_sin_resultados_devuelve_vacio(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = []

        repo = RepositorioNotificacionesPostgres()

        assert repo.obtener_polizas_alertables_renovacion() == []


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestBuscarNotificacionesPorPoliza:

    def test_filtra_por_numero_poliza(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = [FILA_NOTIFICACION]

        repo = RepositorioNotificacionesPostgres()
        notificaciones = repo.buscar_notificaciones_por_poliza('POL-001')

        query, params = cursor.execute.call_args.args
        assert 'N.numero_poliza = %(numero_poliza)s' in str(query)
        assert params == {'numero_poliza': 'POL-001'}
        assert len(notificaciones) == 1
        assert notificaciones[0].numero_poliza == 'POL-001'
        assert notificaciones[0].codigo_tipo == 'RENOVACION_GESTION_PENDIENTE'

    def test_sin_resultados_devuelve_vacio(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = []

        repo = RepositorioNotificacionesPostgres()

        assert repo.buscar_notificaciones_por_poliza('POL-404') == []
