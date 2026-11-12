from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.solicitud_cotizacion.dto.filtro_panel_cotizaciones import (
    FiltroPanelCotizaciones,
)
from app.dominio.cotizacion.servicio_estado_cotizacion import (
    INTERVALO_VENCIMIENTO_DIAS,
)
from app.infraestructura.solicitud_cotizacion.servicios.consulta_panel_cotizaciones_postgres_service import (
    ConsultaPanelCotizacionesPostgresService,
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


def _sql_de(ejecucion) -> str:
    return ejecucion.args[0].as_string(None)


FILA_DB = {
    'id': 1,
    'id_prospecto': 101,
    'id_proceso_comercial': 202,
    'cliente': 'Condominio Las Torres',
    'linea_seguro': 'Incendio Condominio',
    'ejecutivo_comercial': 'Ana Pérez',
    'prioridad': 'alta',
    'fecha': '2026-11-10T10:00:00',
    'cantidad_cotizaciones': 1,
    'vencimiento_mas_proximo': '2026-12-01T00:00:00',
    'estado': 'VIGENTE',
    'tiene_estudio': False,
    'id_estudio': None,
    'cotizaciones': [
        {
            'id': 11,
            'company': 'Company',
            'prima_neta': 10.0,
            'prima_bruta': 11.9,
            'fecha_vencimiento': '2026-12-01T00:00:00',
            'estado': 'VIGENTE',
        }
    ],
}


@patch(
    'app.infraestructura.solicitud_cotizacion.servicios.consulta_panel_cotizaciones_postgres_service.obtener_conexion'
)
@pytest.mark.unit
class TestConsultaPanelCotizacionesListar:

    def test_listar_ejecuta_total_y_datos_con_resumen_embebido(
        self, obtener_conexion_mock
    ):
        conexion, cursor = _conexion_mock(rows=[FILA_DB], row={'total': 23})
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        filas, total = servicio.listar(None, FiltroPanelCotizaciones())

        assert total == 23
        assert len(filas) == 1
        assert filas[0].cliente == 'Condominio Las Torres'
        assert filas[0].cotizaciones[0].company == 'Company'
        assert filas[0].cotizaciones[0].estado == 'VIGENTE'

        assert cursor.execute.call_count == 2
        sql_total = _sql_de(cursor.execute.call_args_list[0])
        sql_datos = _sql_de(cursor.execute.call_args_list[1])

        # La query de datos trae el resumen en un solo json_agg (sin N+1) y el
        # total sale de una query liviana sin construir el JSON.
        assert 'json_agg' in sql_datos
        assert 'json_agg' not in sql_total
        assert "'prima_neta'" in sql_datos

    def test_referencias_del_lateral_van_sin_citar(self, obtener_conexion_mock):
        # Regresión: los alias del lateral se pliegan a minúsculas en Postgres
        # (from Cotizacion C => c), así que el CASE del estado debe emitir
        # C.fecha_emision sin citar; un "C" citado rompía la query de datos.
        conexion, cursor = _conexion_mock(rows=[], row={'total': 0})
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.listar(None, FiltroPanelCotizaciones())

        sql_datos = _sql_de(cursor.execute.call_args_list[1])

        assert '"C".' not in sql_datos
        assert '"COT".' not in sql_datos
        assert 'C."fecha_emision"' in sql_datos
        assert 'COT.cot_vencimiento' in sql_datos

    def test_los_estados_se_califican_con_el_mismo_ahora(
        self, obtener_conexion_mock
    ):
        conexion, cursor = _conexion_mock(rows=[], row={'total': 0})
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.listar(None, FiltroPanelCotizaciones())

        for ejecucion in cursor.execute.call_args_list:
            params = ejecucion.args[1]
            assert 'ahora' in params
            assert params['intervalo_vencimiento'] == INTERVALO_VENCIMIENTO_DIAS

    def test_paginacion_viaja_en_los_params(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(rows=[], row={'total': 0})
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.listar(None, FiltroPanelCotizaciones(pagina=3, tamano_pagina=5))

        params_datos = cursor.execute.call_args_list[1].args[1]
        assert params_datos['tamano_pagina'] == 5
        assert params_datos['offset'] == 10

    def test_texto_busqueda_compara_cliente_producto_y_ejecutivo(
        self, obtener_conexion_mock
    ):
        conexion, cursor = _conexion_mock(rows=[], row={'total': 0})
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.listar(None, FiltroPanelCotizaciones(texto_busqueda='tor_res'))

        sql_datos = _sql_de(cursor.execute.call_args_list[1]).lower()
        assert 'unaccent(lower(p.nombre_riesgo))' in sql_datos
        assert 'unaccent(lower(pr.nombre))' in sql_datos
        assert 'unaccent(lower(ej_com.nombre))' in sql_datos

        params_datos = cursor.execute.call_args_list[1].args[1]
        assert params_datos['texto_busqueda'] == '%tor\\_res%'

    @pytest.mark.parametrize(
        ('estado', 'fragmento'),
        [
            ('cotizaciones_vigentes', "= 'VIGENTE'"),
            ('cotizaciones_por_vencer', "= 'POR_VENCER'"),
            ('cotizaciones_vencidas', "= 'VENCIDA'"),
            (
                'estudios_pendientes',
                'not exists(select 1 from EstudioComercialCondominio',
            ),
            ('estudios_emitidos', 'exists(select 1 from EstudioComercialCondominio'),
        ],
    )
    def test_filtro_estado_aplica_su_condicion(
        self, obtener_conexion_mock, estado, fragmento
    ):
        conexion, cursor = _conexion_mock(rows=[], row={'total': 0})
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.listar(None, FiltroPanelCotizaciones(estado=estado))

        sql_datos = _sql_de(cursor.execute.call_args_list[1])
        assert fragmento in sql_datos

    def test_filtro_cotizaciones_es_exists_con_estado_propio(self, obtener_conexion_mock):
        # Cada cotización se clasifica por sus propias fechas: la solicitud
        # coincide si tiene al menos una cotización en el estado pedido.
        conexion, cursor = _conexion_mock(rows=[], row={'total': 0})
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.listar(None, FiltroPanelCotizaciones(estado='cotizaciones_vencidas'))

        sql_datos = _sql_de(cursor.execute.call_args_list[1])
        assert 'exists(' in sql_datos
        assert 'select 1 from Cotizacion' in sql_datos
        assert "= 'VENCIDA'" in sql_datos

    def test_filtro_estudios_pendientes_solo_tipos_condominio(
        self, obtener_conexion_mock
    ):
        conexion, cursor = _conexion_mock(rows=[], row={'total': 0})
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.listar(None, FiltroPanelCotizaciones(estado='estudios_pendientes'))

        sql_datos = _sql_de(cursor.execute.call_args_list[1])
        assert "SC.tipo in ('espacios_comunes', 'unidades')" in sql_datos
        assert 'not exists(select 1 from EstudioComercialCondominio' in sql_datos

    def test_rut_ejecutivo_compara_exacto_contra_el_ejecutivo(
        self, obtener_conexion_mock
    ):
        conexion, cursor = _conexion_mock(rows=[], row={'total': 0})
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.listar(None, FiltroPanelCotizaciones(rut_ejecutivo='11111111-1'))

        sql_datos = _sql_de(cursor.execute.call_args_list[1])
        assert 'PC.rut_ej_comercial = %(rut_ejecutivo)s' in sql_datos
        assert cursor.execute.call_args_list[1].args[1]['rut_ejecutivo'] == '11111111-1'


@patch(
    'app.infraestructura.solicitud_cotizacion.servicios.consulta_panel_cotizaciones_postgres_service.obtener_conexion'
)
@pytest.mark.unit
class TestConsultaPanelCotizacionesContadores:

    def test_contadores_se_calculan_sin_filtros(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock()
        cursor.fetchone.side_effect = [
            {'cotizaciones_vigentes': 0, 'cotizaciones_por_vencer': 0, 'cotizaciones_vencidas': 0},
            {'estudios_emitidos': 0, 'estudios_pendientes': 0},
        ]
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.contadores('11111111-1')

        for ejecucion in cursor.execute.call_args_list:
            params = ejecucion.args[1]
            # Solo el scope por permisos, ningún filtro de búsqueda/estado.
            assert params['rut_scoping'] == '11111111-1'
            assert 'texto_busqueda' not in params
            assert 'prioridad' not in params
            assert 'rut_ejecutivo' not in params

    def test_contadores_cuentan_cada_cotizacion_y_cada_estudio(
        self, obtener_conexion_mock
    ):
        # Ejemplo del panel: una solicitud con 3 cotizaciones vigentes y 1
        # vencida suma 3 y 1; con 2 estudios emitidos suma 2 a emitidos.
        conexion, cursor = _conexion_mock()
        cursor.fetchone.side_effect = [
            {
                'cotizaciones_vigentes': 3,
                'cotizaciones_por_vencer': 0,
                'cotizaciones_vencidas': 1,
            },
            {'estudios_emitidos': 2, 'estudios_pendientes': 4},
        ]
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        contadores = servicio.contadores(None)

        assert contadores.cotizaciones_vigentes == 3
        assert contadores.cotizaciones_vencidas == 1
        assert contadores.estudios_emitidos == 2
        assert contadores.estudios_pendientes == 4

        assert cursor.execute.call_count == 2
        sql_cotizaciones = _sql_de(cursor.execute.call_args_list[0])
        sql_estudios = _sql_de(cursor.execute.call_args_list[1])

        # Cada cotización cuenta individualmente, clasificada por su estado.
        assert 'count(*) filter' in sql_cotizaciones
        assert 'inner join Cotizacion C' in sql_cotizaciones
        # El CASE referencia el alias sin citar (la columna citada en
        # minúscula sí resuelve: casa con el nombre plegado).
        assert 'C."fecha_emision"' in sql_cotizaciones
        assert '"C".' not in sql_cotizaciones
        # Cada estudio emitido cuenta individualmente.
        assert 'sum((select count(*) from EstudioComercialCondominio' in sql_estudios
        # Pendientes solo para los productos que requieren estudio.
        assert "SC.tipo in ('espacios_comunes', 'unidades')" in sql_estudios
        # Sin resumen JSON: los contadores no lo necesitan.
        assert 'json_agg' not in sql_cotizaciones
        assert 'json_agg' not in sql_estudios

    def test_contadores_usan_el_mismo_ahora_que_los_datos(
        self, obtener_conexion_mock
    ):
        conexion, cursor = _conexion_mock()
        cursor.fetchone.side_effect = [
            {'cotizaciones_vigentes': 0, 'cotizaciones_por_vencer': 0, 'cotizaciones_vencidas': 0},
            {'estudios_emitidos': 0, 'estudios_pendientes': 0},
        ]
        obtener_conexion_mock.return_value = conexion

        servicio = ConsultaPanelCotizacionesPostgresService()
        servicio.contadores(None)

        for ejecucion in cursor.execute.call_args_list:
            params = ejecucion.args[1]
            assert 'ahora' in params
            assert params['intervalo_vencimiento'] == INTERVALO_VENCIMIENTO_DIAS
