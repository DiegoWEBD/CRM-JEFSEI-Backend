from unittest.mock import MagicMock

import pytest

from app.aplicacion.solicitud_cotizacion.use_cases.importar_alicuotas.dto.configuracion_importacion_alicuotas import (
    ConfiguracionImportacionAlicuotas,
)
from app.aplicacion.solicitud_cotizacion.use_cases.importar_alicuotas.validar_alicuotas import (
    ValidarAlicuotasUseCase,
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


def _fila(identificador, prorrateo, formato=None):
    return [
        CeldaExcel(valor=identificador),
        CeldaExcel(valor=prorrateo, formato_numerico=formato),
    ]


def _config(**cambios):
    datos = {
        'hoja': 'Hoja1',
        'fila_encabezados': 1,
        'columna_identificador': 1,
        'columna_prorrateo': 2,
        'primera_fila': 2,
        'ultima_fila': 3,
        'interpretacion_prorrateo': 'valor_porcentual',
    }
    datos.update(cambios)
    return ConfiguracionImportacionAlicuotas(**datos)


@pytest.mark.unit
class TestValidarAlicuotas:

    def test_extrae_registros_validos(self):
        lector = _lector(
            [HojaExcel('Hoja1', 3, 2)],
            [_fila('Depto 1', 2.5), _fila('Depto 2', 1.5)],
        )

        resultado = ValidarAlicuotasUseCase(lector).ejecutar(b'archivo', _config())

        assert resultado['cantidad_registros'] == 2
        assert resultado['registros'][0]['identificador_unidad'] == 'Depto 1'
        assert resultado['registros'][0]['prorrateo'] == 2.5
        assert resultado['suma_prorrateos'] == 4.0
        assert resultado['tiene_errores_bloqueantes'] is False

    def test_pide_el_rango_al_lector(self):
        lector = _lector(
            [HojaExcel('Hoja1', 3, 2)],
            [_fila('Depto 1', 2.5)],
        )

        ValidarAlicuotasUseCase(lector).ejecutar(b'archivo', _config())

        lector.leer_bloque.assert_called_once_with(b'archivo', 'Hoja1', 2, 3, [1, 2])

    def test_reporta_errores_por_fila(self):
        lector = _lector(
            [HojaExcel('Hoja1', 3, 2)],
            [_fila('Depto 1', None), _fila('Depto 2', 1.5)],
        )

        resultado = ValidarAlicuotasUseCase(lector).ejecutar(b'archivo', _config())

        assert resultado['tiene_errores_bloqueantes'] is True
        assert resultado['problemas'][0]['fila_origen'] == 2

    def test_interpretacion_pendiente_se_reporta(self):
        lector = _lector(
            [HojaExcel('Hoja1', 2, 2)],
            [_fila('Depto 1', 0.85)],
        )

        resultado = ValidarAlicuotasUseCase(lector).ejecutar(
            b'archivo', _config(ultima_fila=2, interpretacion_prorrateo=None)
        )

        assert resultado['confirmacion_requerida'] is True
        assert resultado['registros'][0]['estado'] == 'pendiente'
        assert resultado['registros'][0]['prorrateo'] is None

    def test_hoja_inexistente_es_rechazada(self):
        lector = _lector([HojaExcel('Hoja1', 3, 2)])

        with pytest.raises(DatoInvalidoException):
            ValidarAlicuotasUseCase(lector).ejecutar(b'archivo', _config(hoja='NoExiste'))

    def test_rango_invertido_es_rechazado(self):
        lector = _lector([HojaExcel('Hoja1', 3, 2)])

        with pytest.raises(DatoInvalidoException):
            ValidarAlicuotasUseCase(lector).ejecutar(b'archivo', _config(primera_fila=3, ultima_fila=2))

    def test_primera_fila_debe_ser_posterior_a_encabezados(self):
        lector = _lector([HojaExcel('Hoja1', 3, 2)])

        with pytest.raises(DatoInvalidoException):
            ValidarAlicuotasUseCase(lector).ejecutar(b'archivo', _config(primera_fila=1))

    def test_rango_fuera_de_la_hoja_es_rechazado(self):
        lector = _lector([HojaExcel('Hoja1', 3, 2)])

        with pytest.raises(DatoInvalidoException):
            ValidarAlicuotasUseCase(lector).ejecutar(b'archivo', _config(ultima_fila=9))

    def test_columna_fuera_de_limites_es_rechazada(self):
        lector = _lector([HojaExcel('Hoja1', 3, 2)])

        with pytest.raises(DatoInvalidoException):
            ValidarAlicuotasUseCase(lector).ejecutar(b'archivo', _config(columna_prorrateo=5))

    def test_columnas_iguales_son_rechazadas(self):
        lector = _lector([HojaExcel('Hoja1', 3, 2)])

        with pytest.raises(DatoInvalidoException):
            ValidarAlicuotasUseCase(lector).ejecutar(b'archivo', _config(columna_prorrateo=1))

    def test_interpretacion_desconocida_es_rechazada(self):
        lector = _lector([HojaExcel('Hoja1', 3, 2)])

        with pytest.raises(DatoInvalidoException):
            ValidarAlicuotasUseCase(lector).ejecutar(
                b'archivo', _config(interpretacion_prorrateo='inventada')
            )
