from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import (
    RepositorioProcesosComercialesPostgres,
)

MODULO = 'app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres'

CONTADORES = {
    'total': 0,
    'abiertos': 0,
    'ganados': 0,
    'perdidos': 0,
    'verde': 0,
    'amarillo': 0,
    'rojo': 0,
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
class TestSemaforoReporteUsaTransicionPrincipal:

    def test_el_dias_limite_del_semaforo_viene_de_la_transicion_principal(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = CONTADORES
        cursor.fetchall.return_value = []

        repo = RepositorioProcesosComercialesPostgres()
        repo.obtener_todos()

        query_str = str(cursor.execute.call_args_list[0].args[0])
        assert 'LEFT JOIN TransicionEstadoProcesoComercial T' in query_str
        assert 'T.codigo_estado_origen = EI.codigo' in query_str
        assert 'T.es_principal = true' in query_str
        assert 'T.dias_limite AS dias_limite_transicion' in query_str
        # El límite de la etapa sigue disponible como metadata de etapa_actual,
        # pero el semáforo no debe calcularse con él.
        assert 'base.dias_limite_etapa' not in query_str

    def test_los_dias_se_miden_desde_el_ingreso_al_estado_actual(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = CONTADORES
        cursor.fetchall.return_value = []

        repo = RepositorioProcesosComercialesPostgres()
        repo.obtener_todos()

        query_str = str(cursor.execute.call_args_list[0].args[0])
        assert 'HI.fecha_registro AS fecha_ingreso_estado' in query_str
        assert 'fecha_ingreso_etapa' not in query_str

    def test_umbrales_y_guardia_de_sla_sin_limite(self, mock_conexion):
        """Mismos umbrales que las alertas: VERDE < 70%, AMARILLO <= 100%, ROJO > 100%.

        Sin transición principal, sin límite o con límite <= 0 -> NO_APLICA
        (misma semántica que 'sin límite -> sin alerta').
        """
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = CONTADORES
        cursor.fetchall.return_value = []

        repo = RepositorioProcesosComercialesPostgres()
        repo.obtener_todos()

        query_str = str(cursor.execute.call_args_list[0].args[0])
        assert 'dias_limite_transicion <= 0' in query_str
        assert '< 0.70' in query_str
        assert '<= 1.0' in query_str

    def test_filtro_de_fecha_filtra_sobre_ingreso_al_estado(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = CONTADORES
        cursor.fetchall.return_value = []

        repo = RepositorioProcesosComercialesPostgres()
        repo.obtener_todos(fecha_ingreso_etapa_desde='2026-01-01')

        data_query_str = str(cursor.execute.call_args_list[2].args[0])
        assert 'base.fecha_ingreso_estado >= %(fecha_desde)s' in data_query_str
        assert 'base.fecha_ingreso_etapa' not in data_query_str
