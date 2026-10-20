import pytest

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.validador_alicuotas import (
    validar_unidades,
)


def _unidad(identificador, prorrateo, fila=2):
    return UnidadAlicuota(
        identificador_unidad=identificador,
        prorrateo=prorrateo,
        fila_origen=fila,
    )


@pytest.mark.unit
class TestValidarUnidades:

    def test_unidades_validas_no_tienen_problemas(self):
        problemas = validar_unidades([
            _unidad('Depto 1', 0.125),
            _unidad('Depto 2', 0.075, fila=3),
        ])

        assert problemas == []

    def test_lista_vacia_es_problema(self):
        problemas = validar_unidades([])

        assert len(problemas) == 1

    def test_identificador_vacio_es_error(self):
        problemas = validar_unidades([_unidad('   ', 0.125)])

        assert len(problemas) == 1
        assert problemas[0].severidad == 'error'

    def test_duplicado_es_error(self):
        problemas = validar_unidades([
            _unidad('Depto 1', 0.125),
            _unidad('depto 1', 0.075, fila=3),
        ])

        assert len(problemas) == 1
        assert problemas[0].fila_origen == 3

    def test_prorrateo_negativo_es_error(self):
        problemas = validar_unidades([_unidad('Depto 1', -1)])

        assert len(problemas) == 1

    def test_prorrateo_mayor_que_uno_es_error(self):
        # El prorrateo es la fracción decimal del todo: no puede superar 1 (100 %)
        problemas = validar_unidades([_unidad('Depto 1', 1.5)])

        assert len(problemas) == 1

    def test_fila_origen_invalida_es_error(self):
        problemas = validar_unidades([_unidad('Depto 1', 1, fila=0)])

        assert len(problemas) == 1
