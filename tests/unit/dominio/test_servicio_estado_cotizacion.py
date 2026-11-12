from datetime import datetime, timedelta, timezone

from app.dominio.cotizacion.servicio_estado_cotizacion import (
    INTERVALO_VENCIMIENTO_DIAS,
    calcular_estado_cotizacion,
)

AHORA = datetime(2026, 11, 12, 12, 0, 0, tzinfo=timezone.utc)


def _fechas(emision: timedelta, vencimiento: timedelta) -> tuple[datetime, datetime]:
    return AHORA + emision, AHORA + vencimiento


class TestCalcularEstadoCotizacion:

    def test_emision_futura_es_registrada(self):
        emision, vencimiento = _fechas(timedelta(days=1), timedelta(days=30))

        estado = calcular_estado_cotizacion(emision, vencimiento, AHORA)

        assert estado == 'REGISTRADA'

    def test_vencimiento_en_los_proximos_dias_es_por_vencer(self):
        emision, vencimiento = _fechas(timedelta(days=-10), timedelta(days=5))

        estado = calcular_estado_cotizacion(emision, vencimiento, AHORA)

        assert estado == 'POR_VENCER'

    def test_en_el_limite_del_intervalo_sigue_siendo_por_vencer(self):
        limite = timedelta(days=INTERVALO_VENCIMIENTO_DIAS, hours=23)
        emision, vencimiento = _fechas(timedelta(days=-10), limite)

        estado = calcular_estado_cotizacion(emision, vencimiento, AHORA)

        assert estado == 'POR_VENCER'

    def test_mas_alla_del_intervalo_es_vigente(self):
        emision, vencimiento = _fechas(
            timedelta(days=-10),
            timedelta(days=INTERVALO_VENCIMIENTO_DIAS + 1),
        )

        estado = calcular_estado_cotizacion(emision, vencimiento, AHORA)

        assert estado == 'VIGENTE'

    def test_vencimiento_pasado_es_vencida(self):
        emision, vencimiento = _fechas(timedelta(days=-30), timedelta(days=-1))

        estado = calcular_estado_cotizacion(emision, vencimiento, AHORA)

        assert estado == 'VENCIDA'

    def test_vencimiento_hoy_es_vencida(self):
        emision, vencimiento = _fechas(timedelta(days=-30), timedelta(seconds=-1))

        estado = calcular_estado_cotizacion(emision, vencimiento, AHORA)

        assert estado == 'VENCIDA'
