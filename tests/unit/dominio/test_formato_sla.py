from datetime import datetime, timedelta, timezone

import pytest

from app.dominio.sla.formato_sla import dias_decimales, formatear_dias_horas


@pytest.mark.unit
class TestDiasDecimales:

    def test_media_jornada_es_media_dia(self):
        desde = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)

        assert dias_decimales(desde, desde + timedelta(hours=12)) == 0.5

    def test_conserva_la_fraccion_de_dia(self):
        desde = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)

        assert dias_decimales(desde, desde + timedelta(hours=13)) == pytest.approx(0.5417, abs=1e-4)

    def test_un_dia_completo(self):
        desde = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)

        assert dias_decimales(desde, desde + timedelta(days=1)) == 1.0


@pytest.mark.unit
class TestFormatearDiasHoras:

    def test_dias_y_horas(self):
        assert formatear_dias_horas(0.5417) == '0 días 13 h'

    def test_singular(self):
        assert formatear_dias_horas(1.25) == '1 día 6 h'

    def test_horas_en_cero_se_omiten(self):
        assert formatear_dias_horas(10) == '10 días'
        assert formatear_dias_horas(1) == '1 día'

    def test_redondea_hacia_abajo(self):
        # 13 h 59 min no llega a 14 h.
        assert formatear_dias_horas(13.99 / 24) == '0 días 13 h'

    def test_cero(self):
        assert formatear_dias_horas(0) == '0 días'

    def test_none(self):
        assert formatear_dias_horas(None) == '—'
