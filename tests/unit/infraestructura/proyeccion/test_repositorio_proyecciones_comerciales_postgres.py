from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.dominio.proyeccion.agregado_proyeccion_proceso import AgregadoProyeccionProceso
from app.infraestructura.proyeccion.repositorio_proyecciones_comerciales_postgres import (
    RepositorioProyeccionesComercialesPostgres,
)


def _conexion_mock(rows=None, row=None):
    conexion = MagicMock()
    cursor = MagicMock()
    conexion.__enter__.return_value = conexion
    conexion.__exit__.return_value = False
    conexion.cursor.return_value.__enter__.return_value = cursor
    conexion.cursor.return_value.__exit__.return_value = False
    if rows is not None:
        cursor.fetchall.return_value = rows
    if row is not None:
        cursor.fetchone.return_value = row
    return conexion, cursor


MODULO = (
    'app.infraestructura.proyeccion.'
    'repositorio_proyecciones_comerciales_postgres.obtener_conexion'
)


@patch(MODULO)
@pytest.mark.unit
class TestReglasDeNegocioEnLaConsulta:
    """Las reglas que antes cubría `ServicioProyeccionesComerciales` viven
    ahora en SQL: estas pruebas fijan los predicados que las representan.
    """

    def _consulta_ejecutada(self, obtener_conexion_mock, ejecutar):
        conexion, cursor = _conexion_mock(row={'total': Decimal('0')})
        obtener_conexion_mock.return_value = conexion

        ejecutar()

        return cursor.execute.call_args.args[0]

    def test_solo_cotizaciones_vigentes(self, obtener_conexion_mock):
        repo = RepositorioProyeccionesComercialesPostgres()

        consulta = self._consulta_ejecutada(
            obtener_conexion_mock, repo.prima_cotizada_total_abiertos
        )

        assert 'C.fecha_vencimiento >= now()' in consulta

    def test_solo_oportunidades_abiertas(self, obtener_conexion_mock):
        repo = RepositorioProyeccionesComercialesPostgres()

        consulta = self._consulta_ejecutada(
            obtener_conexion_mock, repo.prima_cotizada_total_abiertos
        )

        assert 'PC.cerrado = false' in consulta

    def test_prima_potencial_es_promedio_de_las_vigentes(self, obtener_conexion_mock):
        repo = RepositorioProyeccionesComercialesPostgres()

        consulta = self._consulta_ejecutada(
            obtener_conexion_mock, repo.prima_potencial_estimada_total_abiertos
        )

        assert 'suma_prima_vigente / cantidad_vigentes' in consulta
        assert 'cantidad_vigentes > 0' in consulta

    def test_prima_esperada_pondera_por_probabilidad_de_cierre(
        self, obtener_conexion_mock
    ):
        repo = RepositorioProyeccionesComercialesPostgres()

        consulta = self._consulta_ejecutada(
            obtener_conexion_mock, repo.prima_esperada_total_abiertos
        )

        assert (
            'coalesce(probabilidad_cierre_ejecutivo, probabilidad_cierre_estado)'
            in consulta
        )

    def test_prima_esperada_usa_potencial_ya_redondeado(self, obtener_conexion_mock):
        """round(potencial_redondeado * probabilidad): el potencial se
        redondea antes de ponderar, igual que el cálculo histórico.
        """
        repo = RepositorioProyeccionesComercialesPostgres()

        consulta = self._consulta_ejecutada(
            obtener_conexion_mock, repo.prima_esperada_total_abiertos
        )

        posicion_potencial = consulta.index('end) * coalesce(')
        assert 'round((suma_prima_vigente / cantidad_vigentes)::numeric, 2)' in consulta
        assert posicion_potencial > 0

    def test_proyeccion_solo_meses_con_oportunidad_aportante(
        self, obtener_conexion_mock
    ):
        repo = RepositorioProyeccionesComercialesPostgres()

        consulta = self._consulta_ejecutada(
            obtener_conexion_mock,
            repo.proyeccion_prima_esperada_por_mes_abiertos,
        )

        assert 'prima_esperada is not null' in consulta
        assert 'fecha_estimada_cierre is not null' in consulta
        assert "to_char(fecha_estimada_cierre, 'YYYY-MM')" in consulta

    def test_los_totales_suman_valores_ya_redondeados(self, obtener_conexion_mock):
        repo = RepositorioProyeccionesComercialesPostgres()

        consulta = self._consulta_ejecutada(
            obtener_conexion_mock, repo.prima_cotizada_total_abiertos
        )

        assert 'round(sum(prima_cotizada), 2)' in consulta


@patch(MODULO)
@pytest.mark.unit
class TestPrimaCotizadaTotalAbiertos:

    def test_devuelve_el_total_como_float(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': Decimal('2377.80')})
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioProyeccionesComercialesPostgres()

        assert repo.prima_cotizada_total_abiertos() == 2377.8

    def test_devuelve_cero_sin_filas(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        cursor.fetchone.return_value = None
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioProyeccionesComercialesPostgres()

        assert repo.prima_cotizada_total_abiertos() == 0.0


@patch(MODULO)
@pytest.mark.unit
class TestProyeccionPrimaEsperadaPorMesAbiertos:

    def test_convierte_decimal_a_float(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(
            rows=[
                {'mes': '2026-01', 'prima_esperada': Decimal('30.00')},
                {'mes': '2026-03', 'prima_esperada': Decimal('70.50')},
            ]
        )
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioProyeccionesComercialesPostgres()

        assert repo.proyeccion_prima_esperada_por_mes_abiertos() == [
            {'mes': '2026-01', 'prima_esperada': 30.0},
            {'mes': '2026-03', 'prima_esperada': 70.5},
        ]


@patch(MODULO)
@pytest.mark.unit
class TestAgregadosPorProceso:

    def test_sin_ids_no_consulta_la_base(self, obtener_conexion_mock):
        repo = RepositorioProyeccionesComercialesPostgres()

        assert repo.agregados_por_proceso([]) == {}
        obtener_conexion_mock.assert_not_called()

    def test_pasa_los_ids_como_parametro(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[])
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioProyeccionesComercialesPostgres()
        repo.agregados_por_proceso([3, 7])

        _, params = cursor.execute.call_args.args
        assert params == {'ids_proceso': [3, 7]}

    def test_mapea_valores_decimal_a_float(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(
            rows=[
                {
                    'id': 3,
                    'prima_cotizada': Decimal('266.45'),
                    'prima_potencial_estimada': Decimal('133.22'),
                    'prima_esperada': Decimal('106.58'),
                },
            ]
        )
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioProyeccionesComercialesPostgres()

        assert repo.agregados_por_proceso([3]) == {
            3: AgregadoProyeccionProceso(
                prima_cotizada=266.45,
                prima_potencial_estimada=133.22,
                prima_esperada=106.58,
            )
        }

    def test_prima_esperada_nula_se_conserva(self, obtener_conexion_mock):
        """Sin probabilidad de cierre la prima esperada es None (no 0),
        igual que el cálculo histórico por proceso.
        """
        conexion, cursor = _conexion_mock(
            rows=[
                {
                    'id': 5,
                    'prima_cotizada': Decimal('10.00'),
                    'prima_potencial_estimada': Decimal('5.00'),
                    'prima_esperada': None,
                },
            ]
        )
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioProyeccionesComercialesPostgres()
        agregados = repo.agregados_por_proceso([5])

        assert agregados[5].prima_esperada is None

    def test_falta_el_resultado_de_un_id(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(
            rows=[
                {
                    'id': 3,
                    'prima_cotizada': Decimal('1.00'),
                    'prima_potencial_estimada': Decimal('1.00'),
                    'prima_esperada': Decimal('1.00'),
                },
            ]
        )
        obtener_conexion_mock.return_value = conexion

        repo = RepositorioProyeccionesComercialesPostgres()
        agregados = repo.agregados_por_proceso([3, 99])

        assert set(agregados) == {3}
