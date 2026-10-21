from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.dominio.cotizacion.cotizacion import Cotizacion
from app.dominio.estudio_comercial.desglose_unidades.calculadora_desglose_unidades import CalculadoraDesgloseUnidades
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.calculadora_desglose_reconstruccion import CalculadoraDesgloseReconstruccion
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.desglose_reconstruccion_unidad import DesgloseReconstruccionUnidad
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


def _item_reconstruccion(
    identificador='Depto 1',
    prorrateo=0.5,
    fila=2,
    monto_reconstruccion=1500.0,
    monto_asegurado_sugerido=1500.0,
    prorrateo_pago=0.5,
) -> DesgloseReconstruccionUnidad:
    return DesgloseReconstruccionUnidad(
        identificador_unidad=identificador,
        prorrateo=prorrateo,
        fila_origen=fila,
        monto_reconstruccion=monto_reconstruccion,
        monto_asegurado_sugerido=monto_asegurado_sugerido,
        prorrateo_pago=prorrateo_pago,
    )


def _desglose_reconstruccion_200_400() -> list[DesgloseReconstruccionUnidad]:
    # sugerido 200 y 400 (total 600) -> prorrateo de pago 1/3 y 2/3
    return CalculadoraDesgloseReconstruccion.calcular(4760.0, [
        UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=0.030456521, fila_origen=2),
        UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=0.069543479, fila_origen=3),
    ])


@pytest.mark.unit
class TestCalcularDesgloseUnidades:

    def test_calcula_las_primas_una_unica_vez_sobre_el_total_sugerido(self):
        # El cálculo único sobre 600 UF da: afecta 0,36 | excenta 1,15 | neta 1,51
        # IVA 0,07 | bruta 1,58 y se reparte por el prorrateo de pago
        cotizacion = _cotizacion()

        desglose = CalculadoraDesgloseUnidades.calcular_desglose_unidades(
            cotizacion, _desglose_reconstruccion_200_400()
        )

        assert [u.identificador_unidad for u in desglose] == ['Depto 1', 'Depto 2']

        unidad = desglose[0]
        assert unidad.prorrateo_pago == pytest.approx(1 / 3)
        assert unidad.monto_asegurado == 200.0
        assert unidad.prima_afecta == 0.12
        assert unidad.prima_excenta == 0.38
        assert unidad.prima_neta == 0.5
        assert unidad.prima_iva == 0.02
        assert unidad.prima_bruta == 0.53

        unidad = desglose[1]
        assert unidad.prorrateo_pago == pytest.approx(2 / 3)
        assert unidad.monto_asegurado == 400.0
        assert unidad.prima_afecta == 0.24
        assert unidad.prima_excenta == 0.77
        assert unidad.prima_neta == 1.01
        assert unidad.prima_iva == 0.05
        assert unidad.prima_bruta == 1.05

    def test_prorrateo_de_pago_difiere_del_prorrateo_de_alicuota(self):
        # Dos unidades con la misma alícuota (0,5) pero distinto monto asegurado
        # sugerido: el reparto de la prima sigue al monto, no a la alícuota
        desglose_reconstruccion = [
            _item_reconstruccion('Depto 1', prorrateo=0.5, fila=2, monto_asegurado_sugerido=200.0, prorrateo_pago=200.0 / 600.0),
            _item_reconstruccion('Depto 2', prorrateo=0.5, fila=3, monto_asegurado_sugerido=400.0, prorrateo_pago=400.0 / 600.0),
        ]

        desglose = CalculadoraDesgloseUnidades.calcular_desglose_unidades(
            _cotizacion(), desglose_reconstruccion
        )

        assert desglose[0].prorrateo == 0.5
        assert desglose[1].prorrateo == 0.5
        assert desglose[0].prorrateo_pago == pytest.approx(1 / 3)
        assert desglose[1].prorrateo_pago == pytest.approx(2 / 3)
        assert desglose[0].prima_afecta == 0.12
        assert desglose[1].prima_afecta == 0.24

    def test_incluye_tasa_politica_y_asistencias_en_el_calculo_unico(self):
        # prima afecta total = 600/1000 x (0,5 + 0,1) + 5 = 5,36
        # prima excenta total = 600 x 1,92 / 1000 + 3 = 4,15
        cotizacion = _cotizacion(
            tasa_afecta=0.5,
            tasa_excenta=1.92,
            tasa_politica=0.1,
            asistencia_afecta=5.0,
            asistencia_excenta=3.0,
        )

        desglose = CalculadoraDesgloseUnidades.calcular_desglose_unidades(
            cotizacion, _desglose_reconstruccion_200_400()
        )

        assert desglose[0].prima_afecta == 1.79
        assert desglose[0].prima_excenta == 1.38
        assert desglose[1].prima_afecta == 3.57
        assert desglose[1].prima_excenta == 2.77

    def test_unidad_sin_monto_asegurado_no_paga_primas(self):
        cotizacion = _cotizacion(asistencia_afecta=5.0, asistencia_excenta=3.0)
        desglose_reconstruccion = [
            _item_reconstruccion(
                'Depto 1', prorrateo=0.0, fila=2,
                monto_reconstruccion=0.0, monto_asegurado_sugerido=0.0, prorrateo_pago=0.0,
            ),
            _item_reconstruccion(
                'Depto 2', prorrateo=0.5, fila=3,
                monto_reconstruccion=2380.0, monto_asegurado_sugerido=2400.0, prorrateo_pago=1.0,
            ),
        ]

        desglose = CalculadoraDesgloseUnidades.calcular_desglose_unidades(
            cotizacion, desglose_reconstruccion
        )

        unidad = desglose[0]
        assert unidad.prorrateo_pago == 0.0
        assert unidad.prima_afecta == 0.0
        assert unidad.prima_excenta == 0.0
        assert unidad.prima_bruta == 0.0

        assert desglose[1].prima_bruta > 0

    def test_las_cuotas_de_las_unidades_suman_las_primas_calculadas(self):
        cotizacion = _cotizacion()

        desglose = CalculadoraDesgloseUnidades.calcular_desglose_unidades(
            cotizacion, _desglose_reconstruccion_200_400()
        )

        # totales del cálculo único sobre 600 UF
        assert sum(u.prima_afecta for u in desglose) == pytest.approx(0.36, abs=0.01)
        assert sum(u.prima_excenta for u in desglose) == pytest.approx(1.15, abs=0.01)
        assert sum(u.prima_neta for u in desglose) == pytest.approx(1.51, abs=0.01)
        assert sum(u.prima_iva for u in desglose) == pytest.approx(0.07, abs=0.01)
        assert sum(u.prima_bruta for u in desglose) == pytest.approx(1.58, abs=0.01)

    def test_cada_unidad_lleva_su_desglose_de_reconstruccion(self):
        desglose = CalculadoraDesgloseUnidades.calcular_desglose_unidades(
            _cotizacion(), _desglose_reconstruccion_200_400()
        )

        assert [(u.monto_reconstruccion, u.monto_asegurado_sugerido) for u in desglose] == [
            (144.97, 200.0),
            (331.03, 400.0),
        ]
