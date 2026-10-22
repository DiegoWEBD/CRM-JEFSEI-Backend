import pytest

from app.dominio.prospecto.prospecto_condominio.servicio_calculo_reconstruccion import ServicioCalculoReconstruccion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.calculadora_desglose_reconstruccion import CalculadoraDesgloseReconstruccion
from app.dominio.unidades.unidad_alicuota import UnidadAlicuota


def _unidad(identificador='Depto 1', prorrateo=0.030456521, fila=2) -> UnidadAlicuota:
    return UnidadAlicuota(
        identificador_unidad=identificador,
        prorrateo=prorrateo,
        fila_origen=fila,
    )


@pytest.mark.unit
class TestRedondearCentenaSuperior:

    def test_redondea_a_la_centena_superior(self):
        assert ServicioCalculoReconstruccion.redondear_centena_superior(1459.78) == 1500

    def test_valor_multiplo_exacto_no_se_incrementa(self):
        assert ServicioCalculoReconstruccion.redondear_centena_superior(1500.0) == 1500

    def test_valor_poco_sobre_el_multiplo_sube_de_centena(self):
        assert ServicioCalculoReconstruccion.redondear_centena_superior(1500.01) == 1600

    def test_valor_menor_a_cien(self):
        assert ServicioCalculoReconstruccion.redondear_centena_superior(0.01) == 100

    def test_cero(self):
        assert ServicioCalculoReconstruccion.redondear_centena_superior(0) == 0

    def test_negativo_no_produce_montos_negativos(self):
        assert ServicioCalculoReconstruccion.redondear_centena_superior(-50.0) == 0


@pytest.mark.unit
class TestCalcularDesgloseReconstruccion:

    def test_monto_de_reconstruccion_es_valor_unidades_por_prorrateo(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [_unidad()])

        assert len(desglose) == 1
        # 4.760 x 0,030456521 = 144,97303996 (sin redondear)
        assert desglose[0].monto_reconstruccion == pytest.approx(144.97303996)
        assert desglose[0].monto_asegurado_sugerido == 200.0

    def test_monto_asegurado_sugerido_es_la_centena_superior(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [
            _unidad('Depto 1', 0.030456521, fila=2),
            _unidad('Depto 2', 0.069543479, fila=3),
        ])

        assert [u.identificador_unidad for u in desglose] == ['Depto 1', 'Depto 2']
        assert desglose[0].monto_reconstruccion == pytest.approx(144.97303996)
        assert desglose[0].monto_asegurado_sugerido == 200.0
        assert desglose[1].monto_reconstruccion == pytest.approx(331.02696004)
        assert desglose[1].monto_asegurado_sugerido == 400.0

    def test_prorrateo_de_pago_es_el_monto_sugerido_sobre_el_total(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [
            _unidad('Depto 1', 0.030456521, fila=2),
            _unidad('Depto 2', 0.069543479, fila=3),
        ])

        assert desglose[0].prorrateo_pago == pytest.approx(200.0 / 600.0)
        assert desglose[1].prorrateo_pago == pytest.approx(400.0 / 600.0)
        assert sum(u.prorrateo_pago for u in desglose) == pytest.approx(1.0)

    def test_conserva_identificador_prorrateo_y_fila(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [_unidad('Depto 7', 0.5, fila=9)])

        assert desglose[0].identificador_unidad == 'Depto 7'
        assert desglose[0].prorrateo == 0.5
        assert desglose[0].fila_origen == 9

    def test_no_modifica_las_unidades_de_origen(self):
        unidad = _unidad()

        CalculadoraDesgloseReconstruccion.calcular(4760.0, [unidad])

        assert unidad.prorrateo == 0.030456521

    def test_prorrateo_cero(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [_unidad(prorrateo=0.0)])

        assert desglose[0].monto_reconstruccion == 0.0
        assert desglose[0].monto_asegurado_sugerido == 0.0
        assert desglose[0].prorrateo_pago == 0.0

    def test_total_monto_asegurado_sugerido(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [
            _unidad('Depto 1', 0.030456521, fila=2),
            _unidad('Depto 2', 0.069543479, fila=3),
        ])

        assert CalculadoraDesgloseReconstruccion.total_monto_asegurado_sugerido(desglose) == 600.0

    def test_to_dict_incluye_los_prorrateos_y_los_montos(self):
        desglose = CalculadoraDesgloseReconstruccion.calcular(4760.0, [_unidad()])

        assert desglose[0].to_dict() == {
            'identificador_unidad': 'Depto 1',
            'prorrateo': 0.030456521,
            'fila_origen': 2,
            'monto_reconstruccion': 144.97303996,
            'monto_asegurado_sugerido': 200.0,
            'prorrateo_pago': 1.0,
        }
