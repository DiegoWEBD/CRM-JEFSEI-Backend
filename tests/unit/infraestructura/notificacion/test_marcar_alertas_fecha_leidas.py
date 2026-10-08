from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.infraestructura.notificacion.alertas_por_proceso import (
    TIPOS_ALERTA_FECHA,
    marcar_alertas_fecha_leidas,
)


@pytest.mark.unit
class TestMarcarAlertasFechaLeidas:

    def test_marca_solo_tipos_fecha(self):
        cur = MagicMock()
        cur.fetchall.return_value = []

        marcar_alertas_fecha_leidas(cur, id_proceso=1, fecha=datetime(2026, 1, 1, tzinfo=timezone.utc))

        query, params = cur.execute.call_args[0]
        assert 'update notificacion' in query.lower()
        assert params['tipos_fecha'] == list(TIPOS_ALERTA_FECHA)
        assert params['id_proceso'] == 1

    def test_retorna_ruts_de_alertas_marcadas(self):
        cur = MagicMock()
        cur.fetchall.return_value = [
            {'rut_usuario': '11111111-1'},
            {'rut_usuario': '22222222-2'},
        ]

        ruts = marcar_alertas_fecha_leidas(cur, id_proceso=1, fecha=datetime(2026, 1, 1, tzinfo=timezone.utc))

        assert ruts == ['11111111-1', '22222222-2']

    def test_excluye_ruts_nulos(self):
        cur = MagicMock()
        cur.fetchall.return_value = [
            {'rut_usuario': '11111111-1'},
            {'rut_usuario': None},
        ]

        ruts = marcar_alertas_fecha_leidas(cur, id_proceso=1, fecha=datetime(2026, 1, 1, tzinfo=timezone.utc))

        assert ruts == ['11111111-1']

    def test_tipos_fecha_incluye_ambos(self):
        assert 'CIERRE_ESTIMADO_PROXIMO' in TIPOS_ALERTA_FECHA
        assert 'FECHA_CIERRE_VENCIDA' in TIPOS_ALERTA_FECHA

    def test_no_incluye_tipos_sla(self):
        assert 'SLA_POR_VENCER' not in TIPOS_ALERTA_FECHA
        assert 'SLA_VENCIDO' not in TIPOS_ALERTA_FECHA
