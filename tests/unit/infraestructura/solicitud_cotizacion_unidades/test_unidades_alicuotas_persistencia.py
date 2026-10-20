from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.unidad_alicuota import UnidadAlicuota
from app.dominio.solicitud_cotizacion.solicitud_cotizacion_unidades.solicitud_cotizacion_unidades import (
    SolicitudCotizacionUnidades,
)
from app.infraestructura.solicitud_cotizacion.repositorio_solicitudes_cotizacion_postgres import (
    RepositorioSolicitudesCotizacionPostgres,
)
from app.infraestructura.solicitud_cotizacion.repositorio_unidades_alicuotas_postgres import (
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


def _solicitud(unidades=None):
    return SolicitudCotizacionUnidades(
        id=None,
        fecha=datetime(2026, 1, 1),
        nombre_riesgo='',
        informacion_completa=False,
        rut_ejecutivo_comercial='1-9',
        nombre_ejecutivo_comercial='1-9',
        prioridad='ALTA',
        observaciones=None,
        tipo='unidades',
        producto='',
        recotizacion=False,
        motivo_recotizacion=None,
        monto_asegurado=None,
        nombre_excel='alicuota.xlsx',
        unidades=unidades,
    )


def _unidades():
    return [
        UnidadAlicuota(identificador_unidad='Depto 1', prorrateo=2.5, fila_origen=2),
        UnidadAlicuota(identificador_unidad='Depto 2', prorrateo=1.5, fila_origen=3),
    ]


@patch(
    'app.infraestructura.solicitud_cotizacion.repositorio_solicitudes_cotizacion_postgres.obtener_conexion'
)
@pytest.mark.unit
class TestNuevaSolicitudConUnidades:

    def test_inserta_las_unidades(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        cursor.fetchone.side_effect = [{'codigo': 'unidades'}, {'id': 10}]
        obtener_conexion_mock.return_value = conexion

        RepositorioSolicitudesCotizacionPostgres().nueva_solicitud(
            solicitud=_solicitud(unidades=_unidades()),
            id_proceso_comercial=42,
            registrado_por=MagicMock(rut='1-9'),
        )

        inserts = [
            str(accion.args[0]).lower()
            for accion in cursor.execute.call_args_list
        ]
        cantidad_unidades = sum(
            1 for query in inserts if 'insert into solicitudcotizacionunidad' in query
        )

        assert cantidad_unidades == 2

        parametros = [
            accion.args[1]
            for accion in cursor.execute.call_args_list
            if 'insert into solicitudcotizacionunidad' in str(accion.args[0]).lower()
        ]
        assert parametros[0] == {
            'id_solicitud': 10,
            'identificador_unidad': 'Depto 1',
            'prorrateo': 2.5,
            'fila_origen': 2,
        }

    def test_todo_ocurre_en_una_unica_transaccion(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        cursor.fetchone.side_effect = [{'codigo': 'unidades'}, {'id': 10}]
        obtener_conexion_mock.return_value = conexion

        RepositorioSolicitudesCotizacionPostgres().nueva_solicitud(
            solicitud=_solicitud(unidades=_unidades()),
            id_proceso_comercial=42,
            registrado_por=MagicMock(rut='1-9'),
        )

        assert obtener_conexion_mock.call_count == 1

    def test_sin_unidades_no_inserta_en_la_tabla_nueva(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        cursor.fetchone.side_effect = [{'codigo': 'unidades'}, {'id': 10}]
        obtener_conexion_mock.return_value = conexion

        RepositorioSolicitudesCotizacionPostgres().nueva_solicitud(
            solicitud=_solicitud(unidades=None),
            id_proceso_comercial=42,
            registrado_por=MagicMock(rut='1-9'),
        )

        inserts = [
            str(accion.args[0]).lower()
            for accion in cursor.execute.call_args_list
        ]
        assert not any('insert into solicitudcotizacionunidad' in query for query in inserts)


@patch(
    'app.infraestructura.solicitud_cotizacion.repositorio_unidades_alicuotas_postgres.obtener_conexion'
)
@pytest.mark.unit
class TestListarUnidadesPorSolicitud:

    def test_devuelve_las_unidades_ordenadas_por_fila(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[
            {'identificador_unidad': 'Depto 1', 'prorrateo': 2.5, 'fila_origen': 2},
            {'identificador_unidad': 'Depto 2', 'prorrateo': 1.5, 'fila_origen': 3},
        ])
        obtener_conexion_mock.return_value = conexion

        unidades = RepositorioUnidadesAlicuotasPostgres().listar_por_solicitud(10)

        query = str(cursor.execute.call_args.args[0]).lower()
        params = cursor.execute.call_args.args[1]

        assert 'select' in query
        assert 'from solicitudcotizacionunidad' in query
        assert params == {'id_solicitud': 10}
        assert [u.identificador_unidad for u in unidades] == ['Depto 1', 'Depto 2']
        assert unidades[0].prorrateo == 2.5

    def test_sin_unidades_devuelve_lista_vacia(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[])
        obtener_conexion_mock.return_value = conexion

        unidades = RepositorioUnidadesAlicuotasPostgres().listar_por_solicitud(10)

        assert unidades == []
