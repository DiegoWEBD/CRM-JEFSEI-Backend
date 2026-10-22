from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.notificacion.repositorio_notificaciones_postgres import (
    RepositorioNotificacionesPostgres,
)

MODULO = 'app.infraestructura.notificacion.repositorio_notificaciones_postgres'

FILA = {
    'id_proceso_comercial': 42,
    'nombre_producto': 'Seguro Integral',
    'id_prospecto': 7,
    'codigo_estado': 'ESTUDIO_DISPONIBLE',
    'nombre_estado': 'Estudio disponible',
    'nombre_etapa': 'Evaluación',
    'nombre_prospecto': 'Cliente SpA',
    'fecha_ingreso_estado': datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
    'dias_limite': 15,
    'rol_responsable': 'EJECUTIVO_COMERCIAL',
    'rut_ej_comercial': '11111111-1',
    'rut_ej_evaluacion': '22222222-2',
    'cerrado': False,
    'codigo_siguiente_estado': 'ESTUDIO_ENVIADO_CLIENTE',
    'nombre_siguiente_estado': 'Estudio enviado al cliente',
    'rol_responsable_siguiente': 'EJECUTIVO_EVALUACION_PROYECTOS',
    'accion_requerida': 'enviar estudio al cliente',
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
class TestObtenerProcesosAlertables:

    def test_el_dias_limite_viene_de_la_transicion_principal(self, mock_conexion):
        """El SLA vive en la transición principal, ya no en el estado."""
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = [FILA]

        repo = RepositorioNotificacionesPostgres()
        procesos = repo.obtener_procesos_alertables()

        query_str = str(cursor.execute.call_args.args[0])
        assert 'T.dias_limite' in query_str
        assert 'EI.dias_limite' not in query_str
        assert 'EPC.dias_limite' not in query_str
        assert 'left join TransicionEstadoProcesoComercial T' in query_str
        assert 'T.es_principal = true' in query_str

        assert len(procesos) == 1
        assert procesos[0].dias_limite == 15
        assert procesos[0].rol_responsable_siguiente == 'EJECUTIVO_EVALUACION_PROYECTOS'

    def test_sin_resultados_devuelve_vacio(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = []

        repo = RepositorioNotificacionesPostgres()

        assert repo.obtener_procesos_alertables() == []
