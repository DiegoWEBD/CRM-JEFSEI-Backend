import pytest

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.celda_excel import CeldaExcel
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.deteccion_encabezados import (
    detectar_encabezados,
    normalizar_texto_encabezado,
)


def _fila(*textos):
    return [CeldaExcel(valor=texto) for texto in textos]


@pytest.mark.unit
class TestNormalizarTextoEncabezado:

    def test_minusculas_acentos_y_espacios(self):
        assert normalizar_texto_encabezado('  NÚMERO  ') == 'numero'
        assert normalizar_texto_encabezado('Alícuota') == 'alicuota'


@pytest.mark.unit
class TestDetectarEncabezados:

    def test_detecta_fila_y_columnas(self):
        filas = [
            _fila('Comunidad Los Alerces', None, None),
            _fila(None, None, None),
            _fila('Departamento', 'Dirección', 'Alícuota'),
        ]

        sugerencias = detectar_encabezados(filas)

        assert sugerencias.fila_encabezados == 3
        assert sugerencias.columna_identificador == 1
        assert sugerencias.columna_prorrateo == 3

    def test_columnas_no_contiguas(self):
        filas = [
            _fila('Unidad', 'Propietario', 'N.º bodega', 'Prorrateo'),
        ]

        sugerencias = detectar_encabezados(filas)

        assert sugerencias.fila_encabezados == 1
        assert sugerencias.columna_identificador == 1
        assert sugerencias.columna_prorrateo == 4

    def test_sin_coincidencias_no_sugiere(self):
        filas = [
            _fila('Concepto', 'Valor', 'Observación'),
            _fila('a', 'b', 'c'),
        ]

        sugerencias = detectar_encabezados(filas)

        assert sugerencias.fila_encabezados is None
        assert sugerencias.columna_identificador is None
        assert sugerencias.columna_prorrateo is None

    def test_multiples_candidatas_no_preselecciona_columna(self):
        filas = [
            _fila('Número de cuenta', 'Unidad', 'Prorrateo'),
        ]

        sugerencias = detectar_encabezados(filas)

        assert sugerencias.fila_encabezados == 1
        assert sugerencias.columna_identificador is None
        assert set(sugerencias.columnas_identificador_candidatas) == {1, 2}

    def test_prefiere_fila_con_coincidencias_en_ambas_categorias(self):
        filas = [
            _fila('Unidad', 'Propietario', None),
            _fila('Oficina', 'RUT', 'Participación'),
        ]

        sugerencias = detectar_encabezados(filas)

        assert sugerencias.fila_encabezados == 2
        assert sugerencias.columna_prorrateo == 3
