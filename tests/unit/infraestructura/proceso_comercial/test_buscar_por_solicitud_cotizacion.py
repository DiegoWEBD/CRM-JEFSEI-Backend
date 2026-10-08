from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import (
    RepositorioProcesosComercialesPostgres,
)

MODULO = 'app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres'


def _conexion_mock():
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    return conexion, cursor


def _fila() -> dict:
    return {
        "id": 42,
        "id_prospecto": 10,
        "nombre_cliente": "Cliente Demo",
        "codigo_estado": "ESTADO_1",
        "nombre_estado": "En gestión",
        "fecha_registro_estado": datetime(2026, 9, 1, 10, 0, 0),
        "codigo_etapa": "ETAPA_1",
        "nombre_etapa": "Prospecto",
        "dias_limite_etapa": 30,
        "cerrado": False,
        "rut_ej_comercial": "12345678-9",
        "nombre_ej_comercial": "Juan Pérez",
        "rut_ej_evaluacion": None,
        "nombre_ej_evaluacion": None,
        "id_producto": 1,
        "codigo_producto": "VIDA-001",
        "nombre_producto": "Seguro de Vida",
        "fecha_estimada_cierre": None,
        "probabilidad_cierre_ejecutivo": None,
        "probabilidad_cierre": 0.05,
    }


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestBuscarPorSolicitudCotizacion:

    def test_resuelve_el_proceso_de_la_solicitud(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = _fila()

        repo = RepositorioProcesosComercialesPostgres()
        proceso = repo.buscar_por_solicitud_cotizacion(3)

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert 'inner join SolicitudCotizacion SC' in query_str
        assert 'SC.id_proceso_comercial = PC.id' in query_str
        assert 'SC.id = %(id_solicitud)s' in query_str
        assert params == {'id_solicitud': 3}
        assert proceso is not None
        assert proceso.id == 42
        assert proceso.id_prospecto == 10

    def test_sin_proceso_devuelve_none(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = None

        repo = RepositorioProcesosComercialesPostgres()

        assert repo.buscar_por_solicitud_cotizacion(99) is None
