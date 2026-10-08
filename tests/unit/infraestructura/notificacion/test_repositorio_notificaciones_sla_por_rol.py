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
    'codigo_tipo': 'SLA_POR_VENCER',
    'nivel': 'AVISO',
    'titulo': 'Oportunidad próximo al límite',
    'mensaje': 'mensaje',
    'entidad_tipo': 'PROCESO_COMERCIAL',
    'entidad_id': 42,
    'id_prospecto': 7,
    'dedupe_key': 'SLA_POR_VENCER:42:CONTACTO_INICIAL:11111111-1',
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
class TestBuscarNotificacionesSlaPorRol:

    def test_filtra_por_prospecto_rol_y_alertas_sla_no_leidas(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = [FILA]

        repo = RepositorioNotificacionesPostgres()
        notificaciones = repo.buscar_notificaciones_sla_por_rol(7, 'EJECUTIVO_COMERCIAL')

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert 'inner join TransicionEstadoProcesoComercial T' in query_str
        assert 'inner join EstadoInformativoProcesoComercial EI_SIGUIENTE' in query_str
        assert "N.entidad_tipo = 'PROCESO_COMERCIAL'" in query_str
        assert 'N.leida = false' in query_str
        assert 'PC.id_prospecto = %(id_prospecto)s' in query_str
        assert 'PC.cerrado = false' in query_str
        assert 'EI_SIGUIENTE.rol_responsable = %(rol)s' in query_str
        assert "'SLA_POR_VENCER'" in query_str
        assert "'SLA_VENCIDO'" in query_str
        assert params == {'id_prospecto': 7, 'rol': 'EJECUTIVO_COMERCIAL'}
        assert len(notificaciones) == 1
        assert notificaciones[0].id == 1
        assert notificaciones[0].rut_usuario == '11111111-1'
        assert notificaciones[0].codigo_tipo == 'SLA_POR_VENCER'

    def test_sin_resultados_devuelve_vacio(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchall.return_value = []

        repo = RepositorioNotificacionesPostgres()

        assert repo.buscar_notificaciones_sla_por_rol(7, 'EJECUTIVO_EVALUACION_PROYECTOS') == []
