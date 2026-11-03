import pytest

from app.dominio.notificacion.tipos_alerta import tipos_resueltos_por


@pytest.mark.unit
class TestTiposResueltosPor:

    def test_gestion_resuelve_la_cotizacion(self):
        assert tipos_resueltos_por(['RENOVACION_GESTION_PENDIENTE']) == (
            'RENOVACION_COTIZACION_PENDIENTE',
        )

    def test_vencida_resuelve_cotizacion_y_gestion(self):
        assert tipos_resueltos_por(['RENOVACION_POLIZA_VENCIDA']) == (
            'RENOVACION_COTIZACION_PENDIENTE',
            'RENOVACION_GESTION_PENDIENTE',
        )

    def test_sla_no_escalona_por_tipo(self):
        # El escalonamiento de alertas SLA por tramos (70/100/130/...) lo hace
        # ServicioAlertasProceso.marcar_leidas_sla_anteriores, no por tipo.
        assert tipos_resueltos_por(['SLA_VENCIDO']) == ()
        assert tipos_resueltos_por(['SLA_POR_VENCER']) == ()

    def test_fecha_cierre_vencida_resuelve_el_por_vencer(self):
        assert tipos_resueltos_por(['FECHA_CIERRE_VENCIDA']) == (
            'CIERRE_ESTIMADO_PROXIMO',
        )

    def test_tipos_sin_escalones_no_resuelven_nada(self):
        assert tipos_resueltos_por(['RENOVACION_COTIZACION_PENDIENTE']) == ()
        assert tipos_resueltos_por(['CIERRE_ESTIMADO_PROXIMO']) == ()
        assert tipos_resueltos_por([]) == ()

    def test_reune_sin_duplicar_los_tipos_de_todo_lo_aplicable(self):
        assert tipos_resueltos_por([
            'RENOVACION_COTIZACION_PENDIENTE',
            'RENOVACION_GESTION_PENDIENTE',
            'RENOVACION_POLIZA_VENCIDA',
        ]) == (
            'RENOVACION_COTIZACION_PENDIENTE',
            'RENOVACION_GESTION_PENDIENTE',
        )
