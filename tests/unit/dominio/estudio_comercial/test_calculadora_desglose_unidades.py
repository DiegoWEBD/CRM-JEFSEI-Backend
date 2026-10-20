from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.desglose_unidades.calculadora_desglose_unidades import CalculadoraDesgloseUnidades
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota


def _cotizacion(
    monto_total_asegurado=41500.0,
    tasa_afecta=0.6,
    tasa_excenta=1.92,
    tasa_politica=0.0,
    asistencia_afecta=0.0,
    asistencia_excenta=0.0,
) -> Cotizacion:
    return Cotizacion(
        id=7,
        monto_total_asegurado=monto_total_asegurado,
        tasa_afecta=tasa_afecta,
        tasa_excenta=tasa_excenta,
        tasa_politica=tasa_politica,
        asistencia_afecta=asistencia_afecta,
        asistencia_excenta=asistencia_excenta,
        company=MagicMock(),
        fecha_emision=datetime(2026, 1, 1),
        fecha_vencimiento=datetime(2026, 12, 31),
        prima_afecta=0.0,
        prima_excenta=0.0,
        prima_neta=0.0,
        prima_iva=0.0,
        prima_bruta=0.0,
    )


def _unidad(identificador='Depto 1', prorrateo=0.030456521, fila=2) -> UnidadAlicuota:
    return UnidadAlicuota(
        identificador_unidad=identificador,
        prorrateo=prorrateo,
        fila_origen=fila,
    )


@pytest.mark.unit
class TestCalcularTotales:

    def test_totales_del_ejemplo_con_tasas(self):
        # 41500 UF, tasa afecta 0,6 y tasa excenta 1,92
        totales = CalculadoraDesgloseUnidades.calcular_totales(_cotizacion())

        assert totales.monto_asegurado == 41500.0
        assert totales.prima_afecta == 24.9
        assert totales.prima_excenta == 79.68
        assert totales.prima_neta == 104.58
        assert totales.prima_iva == 4.73
        assert totales.prima_bruta == 109.31

    def test_totales_con_monto_base_distinto(self):
        # Las tasas de la cotización aplicadas a otro monto (p. ej. el sugerido)
        totales = CalculadoraDesgloseUnidades.calcular_totales(_cotizacion(), monto_base=20000.0)

        assert totales.monto_asegurado == 20000.0
        assert totales.prima_afecta == 12.0
        assert totales.prima_excenta == 38.4
        assert totales.prima_neta == 50.4
        assert totales.prima_iva == 2.28
        assert totales.prima_bruta == 52.68

    def test_totales_incluyen_tasa_politica_y_asistencias(self):
        totales = CalculadoraDesgloseUnidades.calcular_totales(_cotizacion(
            monto_total_asegurado=1000.0,
            tasa_afecta=0.5,
            tasa_excenta=0.0,
            tasa_politica=0.1,
            asistencia_afecta=5.0,
            asistencia_excenta=3.0,
        ))

        assert totales.prima_afecta == 5.6
        assert totales.prima_excenta == 3.0
        assert totales.prima_neta == 8.6
        assert totales.prima_iva == 1.06
        assert totales.prima_bruta == 9.66


@pytest.mark.unit
class TestCalcularDesglose:

    def test_desglose_del_ejemplo_por_unidad(self):
        totales = CalculadoraDesgloseUnidades.calcular_totales(_cotizacion())

        desglose = CalculadoraDesgloseUnidades.calcular_desglose(totales, [_unidad()])

        assert len(desglose) == 1
        unidad = desglose[0]
        assert unidad.identificador_unidad == 'Depto 1'
        assert unidad.prorrateo == 0.030456521
        assert unidad.monto_asegurado == 1263.95
        assert unidad.prima_afecta == 0.76
        assert unidad.prima_excenta == 2.43
        assert unidad.prima_neta == 3.19
        assert unidad.prima_iva == 0.14
        assert unidad.prima_bruta == 3.33

    def test_desglose_de_todas_las_unidades(self):
        totales = CalculadoraDesgloseUnidades.calcular_totales(_cotizacion())

        desglose = CalculadoraDesgloseUnidades.calcular_desglose(totales, [
            _unidad('Depto 1', 0.030456521, fila=2),
            _unidad('Depto 2', 0.069543479, fila=3),
        ])

        assert [u.identificador_unidad for u in desglose] == ['Depto 1', 'Depto 2']

    def test_unidad_con_prorrateo_cero(self):
        totales = CalculadoraDesgloseUnidades.calcular_totales(_cotizacion())

        desglose = CalculadoraDesgloseUnidades.calcular_desglose(totales, [_unidad(prorrateo=0.0)])

        assert desglose[0].monto_asegurado == 0.0
        assert desglose[0].prima_neta == 0.0
        assert desglose[0].prima_iva == 0.0
        assert desglose[0].prima_bruta == 0.0

    def test_prorrateo_total_reconstruye_los_totales(self):
        # La suma de las unidades con prorrateos que cubren el todo
        # aproxima los totales de la cotización (redondeo por unidad)
        totales = CalculadoraDesgloseUnidades.calcular_totales(_cotizacion())

        desglose = CalculadoraDesgloseUnidades.calcular_desglose(totales, [
            _unidad('Depto 1', 0.5),
            _unidad('Depto 2', 0.5),
        ])

        assert sum(u.monto_asegurado for u in desglose) == pytest.approx(41500.0, abs=0.01)
        assert sum(u.prima_bruta for u in desglose) == pytest.approx(109.31, abs=0.01)
