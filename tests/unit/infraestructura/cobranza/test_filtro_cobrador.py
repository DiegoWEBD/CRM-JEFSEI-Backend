import pytest

from app.infraestructura.cobranza.repositorio_consulta_dashboard_cobranza_postgres import (
    _filtro_cobrador,
)


@pytest.mark.unit
class TestFiltroCobrador:

    def test_con_rut_filtra_por_cobrador_asignado(self):
        filtro, params = _filtro_cobrador('11111111-1')

        assert 'rut_ej_cobranza_asignado' in filtro
        assert params == {'rut_usuario': '11111111-1'}

    def test_sin_rut_no_filtra(self):
        filtro, params = _filtro_cobrador(None)

        assert filtro == ''
        assert params == {}
