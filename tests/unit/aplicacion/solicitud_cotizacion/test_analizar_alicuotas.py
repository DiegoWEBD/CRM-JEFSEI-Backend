from unittest.mock import MagicMock

import pytest

from app.aplicacion.solicitud_cotizacion.use_cases.importar_alicuotas.analizar_alicuotas import (
    AnalizarAlicuotasUseCase,
)
from app.dominio.exceptions.dato_invalido_exception import DatoInvalidoException
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.celda_excel import CeldaExcel
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.hoja_excel import HojaExcel
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.lector_alicuotas_excel import (
    LectorAlicuotasExcel,
)


def _lector(hojas, filas_leidas=None):
    lector = MagicMock(spec=LectorAlicuotasExcel)
    lector.obtener_hojas.return_value = hojas
    lector.leer_bloque.return_value = filas_leidas or []
    return lector


def _fila(*valores):
    return [CeldaExcel(valor=v) for v in valores]


@pytest.mark.unit
class TestAnalizarAlicuotas:

    def test_devuelve_hojas_y_selecciona_la_primera(self):
        hojas = [HojaExcel('Alícuotas', 3, 3), HojaExcel('Resumen', 2, 2)]
        lector = _lector(hojas, [_fila('Departamento', 'Dirección', 'Alícuota')])

        resultado = AnalizarAlicuotasUseCase(lector).ejecutar(b'archivo')

        assert [h['nombre'] for h in resultado['hojas']] == ['Alícuotas', 'Resumen']
        assert resultado['hoja_seleccionada'] == 'Alícuotas'
        assert resultado['filas'] == 3
        assert resultado['columnas'] == 3

    def test_permite_seleccionar_la_hoja(self):
        hojas = [HojaExcel('Alícuotas', 3, 3), HojaExcel('Resumen', 2, 2)]
        lector = _lector(hojas, [_fila('Unidad', 'Prorrateo')])

        resultado = AnalizarAlicuotasUseCase(lector).ejecutar(b'archivo', hoja='Resumen')

        assert resultado['hoja_seleccionada'] == 'Resumen'

    def test_devuelve_vista_previa_de_celdas(self):
        hojas = [HojaExcel('Hoja1', 3, 2)]
        lector = _lector(hojas, [_fila('Depto 1', 5), _fila('Depto 2', 6)])

        resultado = AnalizarAlicuotasUseCase(lector).ejecutar(b'archivo', inicio=1, cantidad=2)

        vista = resultado['vista_previa']
        assert vista['fila_desde'] == 1
        assert vista['fila_hasta'] == 2
        assert vista['celdas'][0][0]['valor'] == 'Depto 1'
        assert vista['celdas'][1][1]['valor'] == 6

    def test_devuelve_sugerencias_de_encabezados(self):
        hojas = [HojaExcel('Hoja1', 3, 3)]
        lector = _lector(hojas, [_fila('Departamento', 'Dirección', 'Alícuota')])

        resultado = AnalizarAlicuotasUseCase(lector).ejecutar(b'archivo')

        sugerencias = resultado['sugerencias']
        assert sugerencias['fila_encabezados'] == 1
        assert sugerencias['columna_identificador'] == 1
        assert sugerencias['columna_prorrateo'] == 3

    def test_hoja_inexistente_es_rechazada(self):
        lector = _lector([HojaExcel('Hoja1', 1, 1)])

        with pytest.raises(DatoInvalidoException):
            AnalizarAlicuotasUseCase(lector).ejecutar(b'archivo', hoja='NoExiste')

    def test_archivo_sin_hojas_es_rechazado(self):
        lector = _lector([])

        with pytest.raises(DatoInvalidoException):
            AnalizarAlicuotasUseCase(lector).ejecutar(b'archivo')

    def test_parametros_de_ventana_invalidos_son_rechazados(self):
        lector = _lector([HojaExcel('Hoja1', 3, 3)])

        with pytest.raises(DatoInvalidoException):
            AnalizarAlicuotasUseCase(lector).ejecutar(b'archivo', inicio=0)
