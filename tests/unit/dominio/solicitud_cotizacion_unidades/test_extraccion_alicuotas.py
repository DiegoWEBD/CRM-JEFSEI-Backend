from decimal import Decimal

import pytest

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.celda_excel import CeldaExcel
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.extraccion_alicuotas import (
    ESTADO_ERROR,
    ESTADO_PENDIENTE,
    ESTADO_VALIDO,
    FilaRango,
    extraer_registros,
)
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.interpretacion_prorrateo import (
    VALOR_PORCENTUAL,
)


def _fila(numero, identificador, prorrateo, formato_prorrateo=None, formula_sin_resultado=False):
    return FilaRango(
        numero_fila=numero,
        celda_identificador=CeldaExcel(valor=identificador),
        celda_prorrateo=CeldaExcel(
            valor=prorrateo,
            formato_numerico=formato_prorrateo,
            formula_sin_resultado=formula_sin_resultado,
        ),
    )


def _extraer(*filas, interpretacion_confirmada=VALOR_PORCENTUAL):
    return extraer_registros(list(filas), interpretacion_confirmada=interpretacion_confirmada)


@pytest.mark.unit
class TestExtraerRegistros:

    def test_extrae_registros_validos(self):
        resultado = _extraer(
            _fila(2, 'Depto 101', 12.5),
            _fila(3, 'Depto 102', 7.5),
        )

        assert len(resultado.registros) == 2
        assert resultado.registros[0].fila_origen == 2
        assert resultado.registros[0].identificador_unidad == 'Depto 101'
        assert resultado.registros[0].prorrateo == Decimal('0.125')
        assert resultado.registros[0].estado == ESTADO_VALIDO
        assert resultado.tiene_errores_bloqueantes is False

    def test_identificadores_alfanumericos_y_con_ceros_iniciales(self):
        resultado = _extraer(
            _fila(2, '007', 5),
            _fila(3, 'A-12', 5),
            _fila(4, 42, 5),
        )

        assert [r.identificador_unidad for r in resultado.registros] == ['007', 'A-12', '42']

    def test_identificador_vacio_es_error(self):
        resultado = _extraer(_fila(2, '   ', 5))

        assert resultado.registros[0].estado == ESTADO_ERROR
        assert resultado.tiene_errores_bloqueantes is True
        assert resultado.problemas[0].fila_origen == 2

    def test_identificadores_duplicados_son_error(self):
        resultado = _extraer(
            _fila(2, 'Depto 1', 5),
            _fila(3, '  depto 1 ', 5),
        )

        assert resultado.registros[0].estado == ESTADO_VALIDO
        assert resultado.registros[1].estado == ESTADO_ERROR
        assert resultado.tiene_errores_bloqueantes is True

    def test_prorrateo_vacio_es_error(self):
        resultado = _extraer(_fila(2, 'Depto 1', None))

        assert resultado.registros[0].estado == ESTADO_ERROR

    def test_prorrateo_no_numerico_es_error(self):
        resultado = _extraer(_fila(2, 'Depto 1', 'n/a'))

        assert resultado.registros[0].estado == ESTADO_ERROR

    def test_prorrateo_negativo_es_error(self):
        resultado = _extraer(_fila(2, 'Depto 1', -1.5))

        assert resultado.registros[0].estado == ESTADO_ERROR

    def test_error_de_excel_es_error(self):
        resultado = _extraer(_fila(2, 'Depto 1', '#DIV/0!'))

        assert resultado.registros[0].estado == ESTADO_ERROR

    def test_prorrateo_como_texto_numerico_se_interpreta(self):
        resultado = _extraer(_fila(2, 'Depto 1', '12,5'))

        assert resultado.registros[0].prorrateo == Decimal('0.125')

    def test_formula_sin_resultado_calculado_es_error(self):
        resultado = _extraer(_fila(2, 'Depto 1', None, formula_sin_resultado=True))

        assert resultado.registros[0].estado == ESTADO_ERROR
        assert 'fórmula' in resultado.problemas[0].mensaje

    def test_fila_de_totales_se_excluye_y_se_reporta(self):
        resultado = _extraer(
            _fila(2, 'Depto 1', 5),
            _fila(3, 'TOTAL', 100),
        )

        assert len(resultado.registros) == 1
        assert resultado.filas_excluidas == [3]
        assert resultado.tiene_errores_bloqueantes is True

    def test_prorrateo_normalizado_mayor_que_uno_es_error(self):
        # 150 como valor porcentual normaliza a la fracción 1,5: fuera del rango válido
        resultado = _extraer(_fila(2, 'Depto 1', 150))

        assert resultado.registros[0].estado == ESTADO_ERROR
        assert resultado.registros[0].prorrateo is None

    def test_suma_usa_decimal(self):
        # Diez unidades de 10 % normalizan a 0,1 y suman la fracción decimal 1,0
        resultado = _extraer(*[_fila(2 + i, f'Depto {i}', 10) for i in range(10)])

        assert resultado.suma_prorrateos == Decimal('1.0')

    def test_suma_ignora_filas_con_error(self):
        resultado = _extraer(
            _fila(2, 'Depto 1', 5),
            _fila(3, 'Depto 1', 5),
            _fila(4, 'Depto 2', 2.5),
        )

        assert resultado.suma_prorrateos == Decimal('0.075')

    def test_interpretacion_pendiente_no_normaliza(self):
        resultado = extraer_registros(
            [_fila(2, 'Depto 1', 0.85)],
            interpretacion_confirmada=None,
        )

        assert resultado.interpretacion.requiere_confirmacion is True
        assert resultado.registros[0].estado == ESTADO_PENDIENTE
        assert resultado.registros[0].prorrateo is None
        assert resultado.suma_prorrateos is None
