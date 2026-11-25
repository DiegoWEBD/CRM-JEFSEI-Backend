import pytest
from psycopg import sql

from app.infraestructura.cobranza.repositorio_consulta_dashboard_cobranza_postgres import (
    _filtro_cobrador,
)


@pytest.mark.unit
class TestFiltroCobrador:

    def test_con_rut_filtra_por_cobrador_asignado(self):
        filtro, params = _filtro_cobrador('11111111-1')

        assert isinstance(filtro, sql.Composable)
        assert filtro == sql.SQL(' and C.rut_ej_cobranza_asignado = %(rut_usuario)s')
        assert params == {'rut_usuario': '11111111-1'}

    def test_sin_rut_no_filtra(self):
        filtro, params = _filtro_cobrador(None)

        assert filtro == sql.SQL('')
        assert params == {}

    def test_no_construye_sql_por_concatenacion_de_strings(self):
        # Regla lineamientos §0.2: el fragmento debe ser un composable de psycopg.sql,
        # nunca un str que se concatene a la query.
        filtro, _ = _filtro_cobrador('11111111-1')

        assert not isinstance(filtro, str)
