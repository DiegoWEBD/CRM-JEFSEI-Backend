import pytest

from app.dominio.cotizacion.servicio_calculo_valor_cuota import ServicioCalculoValorCuota
from app.dominio.factor_cuotas_company.factor_cuotas_company import FactorCuotasCompany


@pytest.mark.unit
class TestCalcularValorCuota:

    def test_usa_el_factor_de_la_company_para_la_cantidad_de_cuotas(self):
        factores = [
            FactorCuotasCompany(numero_cuotas=6, factor=1.02),
            FactorCuotasCompany(numero_cuotas=12, factor=1.05),
        ]

        valor_cuota = ServicioCalculoValorCuota.calcular_valor_cuota(100.0, 12, factores)

        assert valor_cuota == 105.0

    def test_sin_factor_para_la_cantidad_usa_formula_generica(self):
        factores = [FactorCuotasCompany(numero_cuotas=6, factor=1.02)]

        valor_cuota = ServicioCalculoValorCuota.calcular_valor_cuota(100.0, 12, factores)

        # cuota = (0,005 x 100) / (1 - 1,005^-12) = 8,6066... -> 8,61
        assert valor_cuota == 8.61

    def test_sin_factores_usa_formula_generica(self):
        valor_cuota = ServicioCalculoValorCuota.calcular_valor_cuota(100.0, 12, [])

        assert valor_cuota == 8.61

    def test_formula_generica(self):
        cuota = ServicioCalculoValorCuota.calcular_con_factor_generico(100.0, 12)

        assert cuota == 8.61

    def test_valor_cuota_redondea_a_dos_decimales(self):
        factores = [FactorCuotasCompany(numero_cuotas=11, factor=1.1)]

        valor_cuota = ServicioCalculoValorCuota.calcular_valor_cuota(0.53, 11, factores)

        assert valor_cuota == 0.58

    def test_valor_cuota_pesos(self):
        assert ServicioCalculoValorCuota.calcular_valor_cuota_pesos(105.0, 38000.0) == 3990000

    def test_valor_cuota_pesos_redondea_al_entero(self):
        assert ServicioCalculoValorCuota.calcular_valor_cuota_pesos(8.61, 38000.0) == 327180
