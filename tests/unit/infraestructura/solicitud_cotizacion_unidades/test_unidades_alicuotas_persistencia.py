from unittest.mock import MagicMock, patch

import pytest

from app.dominio.unidades.unidad_alicuota import UnidadAlicuota
from app.infraestructura.unidades.repositorio_unidades_alicuotas_postgres import (
    RepositorioUnidadesAlicuotasPostgres,
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


def _unidades():
    return [
        UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=0.025, fila_origen=2),
        UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=0.015, fila_origen=3),
    ]


@patch(
    'app.infraestructura.unidades.repositorio_unidades_alicuotas_postgres.obtener_conexion'
)
@pytest.mark.unit
class TestListarUnidadesPorOportunidad:

    def test_devuelve_las_unidades_ordenadas_por_fila(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[
            {'identificador_unidad': 'Depto 1', 'prorrateo': 0.025, 'fila_origen': 2},
            {'identificador_unidad': 'Depto 2', 'prorrateo': 0.015, 'fila_origen': 3},
        ])
        obtener_conexion_mock.return_value = conexion

        unidades = RepositorioUnidadesAlicuotasPostgres().listar_por_oportunidad(42)

        query = str(cursor.execute.call_args.args[0]).lower()
        params = cursor.execute.call_args.args[1]

        assert 'select' in query
        assert 'from procesocomercialunidad' in query
        assert params == {'id_proceso_comercial': 42}
        assert [u.identificador_unidad for u in unidades] == ['Depto 1', 'Depto 2']
        assert unidades[0].prorrateo == 0.025

    def test_sin_unidades_devuelve_lista_vacia(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[])
        obtener_conexion_mock.return_value = conexion

        unidades = RepositorioUnidadesAlicuotasPostgres().listar_por_oportunidad(42)

        assert unidades == []


@patch(
    'app.infraestructura.unidades.repositorio_unidades_alicuotas_postgres.obtener_conexion'
)
@pytest.mark.unit
class TestObtenerNombreExcel:

    def test_devuelve_el_nombre_del_archivo(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'nombre_excel_alicuota': 'alicuota.xlsx'})
        obtener_conexion_mock.return_value = conexion

        nombre = RepositorioUnidadesAlicuotasPostgres().obtener_nombre_excel(42)

        assert nombre == 'alicuota.xlsx'

    def test_sin_alicuota_devuelve_nulo(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'nombre_excel_alicuota': None})
        obtener_conexion_mock.return_value = conexion

        nombre = RepositorioUnidadesAlicuotasPostgres().obtener_nombre_excel(42)

        assert nombre is None


@patch(
    'app.infraestructura.unidades.repositorio_unidades_alicuotas_postgres.obtener_conexion'
)
@pytest.mark.unit
class TestGuardarOReemplazar:

    def test_elimina_previas_e_inserta_las_unidades(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        RepositorioUnidadesAlicuotasPostgres().guardar_o_reemplazar(
            42, 'alicuota.xlsx', _unidades()
        )

        queries = [str(accion.args[0]).lower() for accion in cursor.execute.call_args_list]

        assert any('delete from procesocomercialunidad' in query for query in queries)
        assert sum(1 for query in queries if 'insert into procesocomercialunidad' in query) == 2

        parametros = [
            accion.args[1]
            for accion in cursor.execute.call_args_list
            if 'insert into procesocomercialunidad' in str(accion.args[0]).lower()
        ]
        assert parametros[0] == {
            'id_proceso_comercial': 42,
            'identificador_unidad': 'Depto 1',
            'prorrateo': 0.025,
            'fila_origen': 2,
        }

    def test_actualiza_el_nombre_del_archivo(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        RepositorioUnidadesAlicuotasPostgres().guardar_o_reemplazar(
            42, 'alicuota.xlsx', _unidades()
        )

        updates = [
            accion
            for accion in cursor.execute.call_args_list
            if 'update procesocomercial' in str(accion.args[0]).lower()
        ]

        assert len(updates) == 1
        assert updates[0].args[1] == {
            'nombre_excel': 'alicuota.xlsx',
            'id_proceso_comercial': 42,
        }

    def test_todo_ocurre_en_una_unica_transaccion(self, obtener_conexion_mock):
        conexion, _ = _conexion_mock()
        obtener_conexion_mock.return_value = conexion

        RepositorioUnidadesAlicuotasPostgres().guardar_o_reemplazar(
            42, 'alicuota.xlsx', _unidades()
        )

        assert obtener_conexion_mock.call_count == 1
