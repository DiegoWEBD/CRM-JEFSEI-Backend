from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.solicitud_cotizacion.dto.contadores_solicitudes_cotizacion import (
    ContadoresSolicitudesCotizacion,
)
from app.aplicacion.solicitud_cotizacion.dto.filtro_solicitudes_cotizacion import (
    FiltroSolicitudesCotizacion,
)
from app.infraestructura.solicitud_cotizacion.servicios.consulta_solicitudes_cotizacion_postgres_service import (
    ConsultaSolicitudesCotizacionPostgresService,
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


def _consulta(cursor, indice: int) -> str:
    return str(cursor.execute.call_args_list[indice].args[0])


def _params(cursor, indice: int) -> dict:
    return cursor.execute.call_args_list[indice].args[1]


def _norm(query: str) -> str:
    return query.lower().replace(' ', '').replace('\n', '')


def _where(query: str) -> str:
    """Extrae solo la cláusula WHERE principal (desde el scope hasta order by)."""
    texto = _norm(query)
    inicio = texto.find('wherenotpc.cerrado')
    fin = texto.find('orderby')
    return texto[inicio:fin] if fin != -1 else texto[inicio:]


FILA_RESUMEN = {
    'id': 1,
    'id_prospecto': 10,
    'nombre_riesgo': 'Condominio Las Torres',
    'informacion_completa': False,
    'ejecutivo_comercial': 'Ana Pérez',
    'tipo': 'incendio',
    'recotizacion': False,
    'motivo_recotizacion': None,
    'producto': 'Incendio Condominio',
    'prioridad': 'alta',
    'fecha': '2026-11-10T10:00:00',
    'estudio_disponible': False,
    'tiene_cotizaciones': True,
}


@patch(
    'app.infraestructura.solicitud_cotizacion.servicios.'
    'consulta_solicitudes_cotizacion_postgres_service.obtener_conexion'
)
@pytest.mark.unit
class TestListarSolicitudesCotizacion:

    def test_ejecuta_count_y_select_con_limit_offset(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 42})
        cursor.fetchall.return_value = [FILA_RESUMEN]
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        solicitudes, total = service.listar(None, FiltroSolicitudesCotizacion())

        assert total == 42
        assert len(solicitudes) == 1

        count_query = _consulta(cursor, 0)
        data_query = _consulta(cursor, 1)

        assert 'count(*)' in count_query.lower()
        assert 'limit%(tamano_pagina)soffset%(offset)s' in _norm(data_query)
        assert _params(cursor, 1)['tamano_pagina'] == 15
        assert _params(cursor, 1)['offset'] == 0

    def test_offset_es_pagina_menos_1_multiplicado_por_tamano(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 100})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(
            None,
            FiltroSolicitudesCotizacion(pagina=3, tamano_pagina=25),
        )

        assert _params(cursor, 1)['offset'] == 50
        assert _params(cursor, 1)['tamano_pagina'] == 25

    def test_select_usa_exists_en_vez_de_count_y_sin_join_fanout(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 1})
        cursor.fetchall.return_value = [FILA_RESUMEN]
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(None, FiltroSolicitudesCotizacion())

        data_query = _norm(_consulta(cursor, 1))

        assert 'exists(select1fromcotizacion' in data_query
        assert 'exists(select1fromestudiocomercialcondominio' in data_query
        assert 'astiene_cotizaciones' in data_query
        assert 'asestudio_disponible' in data_query
        assert 'count(c.id)' not in data_query
        assert 'leftjoinestudiocomercialcondominio' not in data_query
        assert 'leftjoincotizacion' not in data_query
        assert 'groupby' not in data_query

    def test_orden_por_fecha_desc(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 1})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(None, FiltroSolicitudesCotizacion())

        assert 'orderbysc.fechadesc' in _norm(_consulta(cursor, 1))

    def test_mapea_filas_a_resumen_con_tiene_cotizaciones(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 1})
        cursor.fetchall.return_value = [FILA_RESUMEN]
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        solicitudes, _ = service.listar(None, FiltroSolicitudesCotizacion())

        resumen = solicitudes[0]
        assert resumen.id == 1
        assert resumen.nombre_riesgo == 'Condominio Las Torres'
        assert resumen.tiene_cotizaciones is True
        assert resumen.estudio_disponible is False
        assert resumen.prioridad == 'alta'


@patch(
    'app.infraestructura.solicitud_cotizacion.servicios.'
    'consulta_solicitudes_cotizacion_postgres_service.obtener_conexion'
)
@pytest.mark.unit
class TestFiltrosListarSolicitudes:

    def test_texto_busqueda_unaccent_lower_sobre_tres_columnas(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(None, FiltroSolicitudesCotizacion(texto_busqueda='San José'))

        where = _where(_consulta(cursor, 1))

        assert 'unaccent(lower(p.nombre_riesgo))likeunaccent(lower(%(texto_busqueda)s))' in where
        assert 'unaccent(lower(pr.nombre))likeunaccent(lower(%(texto_busqueda)s))' in where
        assert 'unaccent(lower(ej_com.nombre))likeunaccent(lower(%(texto_busqueda)s))' in where
        assert _params(cursor, 1)['texto_busqueda'] == '%san josé%'

    def test_texto_busqueda_escapa_comodines(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(None, FiltroSolicitudesCotizacion(texto_busqueda='100%_a'))

        where = _where(_consulta(cursor, 1))

        assert _params(cursor, 1)['texto_busqueda'] == '%100\\%\\_a%'
        assert "escape'\\'" in where

    def test_sin_texto_busqueda_no_agrega_condicion_like(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(None, FiltroSolicitudesCotizacion(texto_busqueda=None))

        assert 'like' not in _norm(_consulta(cursor, 1))
        assert 'texto_busqueda' not in _params(cursor, 1)

    def test_estado_informacion_incompleta(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(
            None,
            FiltroSolicitudesCotizacion(estado='informacion_incompleta'),
        )

        where = _where(_consulta(cursor, 1))
        assert 'notp.informacion_completa' in where

    def test_estado_listas_para_cotizar(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(
            None,
            FiltroSolicitudesCotizacion(estado='listas_para_cotizar'),
        )

        where = _where(_consulta(cursor, 1))
        assert 'p.informacion_completaandnotexists(select1fromcotizacion' in where

    def test_estado_cotizaciones_emitidas(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(
            None,
            FiltroSolicitudesCotizacion(estado='cotizaciones_emitidas'),
        )

        where = _where(_consulta(cursor, 1))
        assert 'exists(select1fromcotizacion' in where
        assert 'notexists(select1fromcotizacion' not in where

    def test_estado_estudios_emitidos(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(
            None,
            FiltroSolicitudesCotizacion(estado='estudios_emitidos'),
        )

        where = _where(_consulta(cursor, 1))
        assert 'exists(select1fromestudiocomercialcondominio' in where
        assert 'notexists(select1fromestudiocomercialcondominio' not in where

    def test_estado_invalido_lanza_value_error(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        with pytest.raises(ValueError):
            service.listar(None, FiltroSolicitudesCotizacion(estado='lo_que_sea'))

    def test_prioridad_unaccent_lower(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(None, FiltroSolicitudesCotizacion(prioridad='alta'))

        where = _where(_consulta(cursor, 1))
        assert 'unaccent(lower(sc.prioridad))=unaccent(lower(%(prioridad)s))' in where
        assert _params(cursor, 1)['prioridad'] == 'alta'

    def test_prioridad_invalida_lanza_value_error(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        with pytest.raises(ValueError):
            service.listar(None, FiltroSolicitudesCotizacion(prioridad='media'))

    def test_rut_usuario_match_exacto_sin_unaccent(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(None, FiltroSolicitudesCotizacion(rut_usuario='12345678-9'))

        data_query = _norm(_consulta(cursor, 1))
        where = _where(_consulta(cursor, 1))

        assert 'pc.rut_ej_comercial=%(rut_usuario)s' in where
        assert 'unaccent(lower(pc.rut_ej_comercial))' not in data_query
        assert _params(cursor, 1)['rut_usuario'] == '12345678-9'

    def test_filtros_completos_conviven_en_el_mismo_where(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(
            '11111111-1',
            FiltroSolicitudesCotizacion(
                texto_busqueda='torres',
                estado='cotizaciones_emitidas',
                prioridad='normal',
                rut_usuario='12345678-9',
            ),
        )

        where = _where(_consulta(cursor, 1))
        assert 'unaccent(lower(p.nombre_riesgo))' in where
        assert 'exists(select1fromcotizacion' in where
        assert 'unaccent(lower(sc.prioridad))' in where
        assert 'pc.rut_ej_comercial=%(rut_usuario)s' in where

        params = _params(cursor, 1)
        assert params['texto_busqueda'] == '%torres%'
        assert params['prioridad'] == 'normal'
        assert params['rut_usuario'] == '12345678-9'
        assert params['rut_scoping'] == '11111111-1'


@patch(
    'app.infraestructura.solicitud_cotizacion.servicios.'
    'consulta_solicitudes_cotizacion_postgres_service.obtener_conexion'
)
@pytest.mark.unit
class TestScopePermisosSolicitudes:

    def test_scope_en_listar(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar('11111111-1', FiltroSolicitudesCotizacion())

        for indice in (0, 1):
            query = _norm(_consulta(cursor, indice))
            assert 'notpc.cerrado' in query
            assert 'cast(%(rut_scoping)sasvarchar)isnull' in query
            assert 'p.rut_ej_comercial_asignado=%(rut_scoping)s' in query
            assert 'p.rut_ej_evaluacion_asignado=%(rut_scoping)s' in query

    def test_scope_sin_scoping_trae_todo(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(row={'total': 0})
        cursor.fetchall.return_value = []
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.listar(None, FiltroSolicitudesCotizacion())

        assert _params(cursor, 1)['rut_scoping'] is None


@patch(
    'app.infraestructura.solicitud_cotizacion.servicios.'
    'consulta_solicitudes_cotizacion_postgres_service.obtener_conexion'
)
@pytest.mark.unit
class TestContadoresSolicitudesCotizacion:

    def test_una_sola_query_count_filter(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(
            row={
                'informacion_incompleta': 3,
                'listas_para_cotizar': 5,
                'cotizaciones_emitidas': 7,
                'estudios_emitidos': 2,
            }
        )
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        contadores = service.contadores(None)

        assert len(cursor.execute.call_args_list) == 1
        assert contadores == ContadoresSolicitudesCotizacion(
            informacion_incompleta=3,
            listas_para_cotizar=5,
            cotizaciones_emitidas=7,
            estudios_emitidos=2,
        )

        query = _norm(_consulta(cursor, 0))
        assert 'count(*)filter(where' in query
        assert 'asinformacion_incompleta' in query
        assert 'aslistas_para_cotizar' in query
        assert 'ascotizaciones_emitidas' in query
        assert 'asestudios_emitidos' in query

    def test_usa_las_mismas_definiciones_que_los_filtros(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(
            row={
                'informacion_incompleta': 0,
                'listas_para_cotizar': 0,
                'cotizaciones_emitidas': 0,
                'estudios_emitidos': 0,
            }
        )
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.contadores(None)

        query = _norm(_consulta(cursor, 0))
        assert 'notp.informacion_completa' in query
        assert 'notexists(select1fromcotizacion' in query
        assert 'exists(select1fromcotizacion' in query
        assert 'exists(select1fromestudiocomercialcondominio' in query

    def test_no_aplica_filtros_de_listado_ni_paginacion(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(
            row={
                'informacion_incompleta': 0,
                'listas_para_cotizar': 0,
                'cotizaciones_emitidas': 0,
                'estudios_emitidos': 0,
            }
        )
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.contadores('11111111-1')

        query = _norm(_consulta(cursor, 0))
        params = _params(cursor, 0)

        assert 'limit' not in query
        assert 'texto_busqueda' not in params
        assert 'prioridad' not in params
        assert 'rut_usuario' not in params
        assert 'offset' not in params
        assert 'tamano_pagina' not in params

    def test_respeta_scope_de_permisos(self, obtener_conexion_mock):
        conexion, cursor = _conexion_mock(
            row={
                'informacion_incompleta': 0,
                'listas_para_cotizar': 0,
                'cotizaciones_emitidas': 0,
                'estudios_emitidos': 0,
            }
        )
        obtener_conexion_mock.return_value = conexion

        service = ConsultaSolicitudesCotizacionPostgresService()
        service.contadores('11111111-1')

        query = _norm(_consulta(cursor, 0))
        assert 'notpc.cerrado' in query
        assert 'cast(%(rut_scoping)sasvarchar)isnull' in query
        assert _params(cursor, 0)['rut_scoping'] == '11111111-1'
