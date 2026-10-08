from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres import (
    RepositorioProcesosComercialesPostgres,
)

MODULO = 'app.infraestructura.proceso_comercial.repositorio_procesos_comerciales_postgres'

FECHA_NUEVA = datetime(2026, 10, 15, 0, 0, 0, tzinfo=timezone.utc)


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestActualizarFechaEstimadaCierreRepo:

    def test_solo_actualiza_el_registro(self, mock_conexion):
        """El repositorio se limita a persistir: la lógica de alertas vive
        en el caso de uso."""
        conexion = MagicMock()
        cursor = MagicMock()
        conexion.__enter__.return_value = conexion
        conexion.__exit__.return_value = False
        conexion.cursor.return_value.__enter__.return_value = cursor
        conexion.cursor.return_value.__exit__.return_value = False
        mock_conexion.return_value = conexion

        repo = RepositorioProcesosComercialesPostgres()
        repo.actualizar_fecha_estimada_cierre(id=1, fecha=FECHA_NUEVA)

        assert cursor.execute.call_count == 1
        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert 'update ProcesoComercial' in query_str
        assert 'fecha_estimada_cierre = %(fecha)s' in query_str
        assert 'Notificacion' not in query_str
        assert params == {'id': 1, 'fecha': FECHA_NUEVA}

    def test_actualiza_con_fecha_none(self, mock_conexion):
        conexion = MagicMock()
        cursor = MagicMock()
        conexion.__enter__.return_value = conexion
        conexion.__exit__.return_value = False
        conexion.cursor.return_value.__enter__.return_value = cursor
        conexion.cursor.return_value.__exit__.return_value = False
        mock_conexion.return_value = conexion

        repo = RepositorioProcesosComercialesPostgres()
        repo.actualizar_fecha_estimada_cierre(id=1, fecha=None)

        params = cursor.execute.call_args.args[1]
        assert params['fecha'] is None
