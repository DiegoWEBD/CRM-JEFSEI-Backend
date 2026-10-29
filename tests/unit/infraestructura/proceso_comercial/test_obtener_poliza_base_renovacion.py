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


@pytest.mark.unit
@patch(f'{MODULO}.obtener_conexion')
class TestObtenerPolizaBaseRenovacion:

    def test_resuelve_la_poliza_base_del_proceso(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = {'numero_poliza_base': 'POL-001'}

        repo = RepositorioProcesosComercialesPostgres()
        numero_poliza = repo.obtener_poliza_base_renovacion(7)

        query, params = cursor.execute.call_args.args
        query_str = str(query)
        assert 'ProcesoComercialRenovacion' in query_str
        assert 'PCR.id = %(id_proceso)s' in query_str
        # Sin filtro por descartado: el lookup se usa al descartar el proceso.
        assert 'descartado' not in query_str
        assert params == {'id_proceso': 7}
        assert numero_poliza == 'POL-001'

    def test_sin_enlace_devuelve_none(self, mock_conexion):
        conexion, cursor = _conexion_mock()
        mock_conexion.return_value = conexion
        cursor.fetchone.return_value = None

        repo = RepositorioProcesosComercialesPostgres()

        assert repo.obtener_poliza_base_renovacion(99) is None
