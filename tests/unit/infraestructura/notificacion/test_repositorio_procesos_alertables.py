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
    'rut_ej_comercial': '11111111-1',
    'rut_ej_evaluacion': '22222222-2',
    'cerrado': False,
    'renovacion': False,
    'rut_ej_renovacion': '55555555-5',
    'rut_as_renovacion': '66666666-6',
    'codigo_siguiente_estado': 'ESTUDIO_ENVIADO_CLIENTE',
    'nombre_siguiente_estado': 'Estudio enviado al cliente',
    'roles_responsables': ['EJECUTIVO_EVALUACION_PROYECTOS'],
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
        assert procesos[0].roles_responsables == ['EJECUTIVO_EVALUACION_PROYECTOS']

    def test_los_responsables_vienen_de_la_transicion_filtrados_por_renovacion(
        self, mock_conexion
    ):
        """Los responsables viven en la transición principal, filtrados
        por el tipo de oportunidad (ProcesoComercial.renovacion)."""
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = [FILA]

        repo = RepositorioNotificacionesPostgres()
        procesos = repo.obtener_procesos_alertables()

        query_str = str(cursor.execute.call_args.args[0])
        assert 'RolResponsableTransicion RRT' in query_str
        assert 'RRT.id_transicion = T.id' in query_str
        assert 'RRT.renovacion = PC.renovacion' in query_str
        assert 'PC.renovacion' in query_str
        assert 'rut_ej_renovacion_asignado as rut_ej_renovacion' in query_str
        assert 'rut_as_renovacion_asignado as rut_as_renovacion' in query_str

        assert len(procesos) == 1
        assert procesos[0].renovacion is False
        assert procesos[0].rut_ej_renovacion == '55555555-5'
        assert procesos[0].rut_as_renovacion == '66666666-6'

    def test_sin_resultados_devuelve_vacio(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = []

        repo = RepositorioNotificacionesPostgres()

        assert repo.obtener_procesos_alertables() == []
