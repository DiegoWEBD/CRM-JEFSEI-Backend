from decimal import Decimal

import pytest

from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.interpretacion_prorrateo import (
    FRACCION_DECIMAL,
    PORCENTAJE_EXCEL,
    VALOR_PORCENTUAL,
    interpretar_prorrateo_columna,
    normalizar_prorrateo,
)


@pytest.mark.unit
class TestInterpretarProrrateoColumna:

    def test_formato_porcentaje_de_excel(self):
        # La celda muestra 0,85 % y almacena 0,0085
        resultado = interpretar_prorrateo_columna(
            valores=[0.0085, 0.0015],
            formatos=['0.00%', '0.00%'],
        )

        assert resultado.tipo == PORCENTAJE_EXCEL
        assert resultado.requiere_confirmacion is False

    def test_formato_porcentaje_parcial_no_fuerza_interpretacion(self):
        resultado = interpretar_prorrateo_columna(
            valores=[0.0085, 0.5],
            formatos=['0.00%', 'General'],
        )

        assert resultado.tipo != PORCENTAJE_EXCEL

    def test_valores_mayores_que_uno_son_valor_porcentual(self):
        # Una fracción decimal del todo no puede superar 1
        resultado = interpretar_prorrateo_columna(
            valores=[12.5, 3.25],
            formatos=[None, None],
        )

        assert resultado.tipo == VALOR_PORCENTUAL
        assert resultado.requiere_confirmacion is False

    def test_suma_cerca_de_uno_sugiere_fraccion_pero_pide_confirmacion(self):
        # Suma 1 sin formato de porcentaje: plausible como fracción decimal,
        # pero también como porcentaje directo de un subconjunto de unidades.
        resultado = interpretar_prorrateo_columna(
            valores=[0.6, 0.3, 0.1],
            formatos=[None, None, None],
        )

        assert resultado.tipo == FRACCION_DECIMAL
        assert resultado.requiere_confirmacion is True

    def test_suma_baja_con_valores_pequenos_es_ambigua(self):
        # Podría ser 0,85 % directo o una fracción decimal de otro total
        resultado = interpretar_prorrateo_columna(
            valores=[0.85, 0.15],
            formatos=[None, None],
        )

        assert resultado.requiere_confirmacion is True
        assert resultado.tipo is not None

    def test_valores_vacios_no_tienen_interpretacion(self):
        resultado = interpretar_prorrateo_columna(valores=[], formatos=[])

        assert resultado.tipo is None
        assert resultado.requiere_confirmacion is False

    def test_interpretacion_confirmada_se_respeta(self):
        resultado = interpretar_prorrateo_columna(
            valores=[0.85, 0.15],
            formatos=[None, None],
            interpretacion_confirmada=VALOR_PORCENTUAL,
        )

        assert resultado.tipo == VALOR_PORCENTUAL
        assert resultado.requiere_confirmacion is False

    def test_interpretacion_confirmada_invalida_es_rechazada(self):
        with pytest.raises(DatoInvalidoException):
            interpretar_prorrateo_columna(
                valores=[0.85],
                formatos=[None],
                interpretacion_confirmada='inventada',
            )


@pytest.mark.unit
class TestNormalizarProrrateo:

    def test_porcentaje_excel(self):
        assert normalizar_prorrateo(0.0085, PORCENTAJE_EXCEL) == Decimal('0.85')

    def test_fraccion_decimal(self):
        assert normalizar_prorrateo(0.0085, FRACCION_DECIMAL) == Decimal('0.85')

    def test_valor_porcentual(self):
        assert normalizar_prorrateo(0.85, VALOR_PORCENTUAL) == Decimal('0.85')

    def test_no_pierde_precision(self):
        assert normalizar_prorrateo(0.1, VALOR_PORCENTUAL) * 3 == Decimal('0.3')

    def test_tipo_invalido_es_rechazado(self):
        with pytest.raises(DatoInvalidoException):
            normalizar_prorrateo(1.0, 'inventada')
