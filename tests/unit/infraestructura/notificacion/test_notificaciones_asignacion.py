from unittest.mock import MagicMock

import pytest

from app.infraestructura.notificacion.notificaciones_asignacion import (
    TIPO_ASIGNACION,
    TIPO_DESASIGNACION,
    registrar_notificacion_asignacion,
    registrar_notificacion_desasignacion,
)


@pytest.mark.unit
class TestRegistrarNotificacionAsignacion:

    def test_inserta_notificacion_con_parametros_correctos(self):
        cur = MagicMock()

        registrar_notificacion_asignacion(
            cur,
            rut_asignado='11111111-1',
            detalle_asignacion='ejecutivo comercial',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Cliente Test',
            id_prospecto=10,
        )

        cur.execute.assert_called_once()
        query, params = cur.execute.call_args[0]

        assert 'insert into notificacion' in query.lower()
        assert params['rut_usuario'] == '11111111-1'
        assert params['codigo_tipo'] == TIPO_ASIGNACION
        assert params['nivel'] == 'INFO'
        assert params['entidad_tipo'] == 'PROSPECTO'
        assert params['entidad_id'] == 10
        assert params['id_prospecto'] == 10
        assert 'ejecutivo comercial' in params['titulo']
        assert 'Cliente Test' in params['mensaje']
        assert params['leible'] is True

    def test_dedupe_key_es_unico_por_evento(self):
        cur = MagicMock()

        registrar_notificacion_asignacion(
            cur,
            rut_asignado='11111111-1',
            detalle_asignacion='ejecutivo comercial',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Cliente Test',
            id_prospecto=10,
        )

        _, params = cur.execute.call_args[0]
        assert params['dedupe_key'].startswith(f'{TIPO_ASIGNACION}:PROSPECTO:10:ejecutivo comercial:')

    def test_no_retorna_nada(self):
        cur = MagicMock()

        resultado = registrar_notificacion_asignacion(
            cur,
            rut_asignado='11111111-1',
            detalle_asignacion='asistente de renovación',
            entidad_tipo='CLIENTE',
            entidad_id=5,
            nombre_entidad='Cliente ABC',
            id_prospecto=3,
        )

        assert resultado is None

    def test_mensaje_incluye_detalle_y_entidad(self):
        cur = MagicMock()

        registrar_notificacion_asignacion(
            cur,
            rut_asignado='22222222-2',
            detalle_asignacion='asistente de renovación',
            entidad_tipo='CLIENTE',
            entidad_id=5,
            nombre_entidad='Empresa XYZ',
            id_prospecto=3,
        )

        _, params = cur.execute.call_args[0]
        assert 'asistente de renovación' in params['mensaje']
        assert 'Empresa XYZ' in params['mensaje']


@pytest.mark.unit
class TestRegistrarNotificacionDesasignacion:

    def test_inserta_notificacion_con_parametros_correctos(self):
        cur = MagicMock()

        registrar_notificacion_desasignacion(
            cur,
            rut_desasignado='11111111-1',
            detalle_asignacion='gestión comercial',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Cliente Test',
            id_prospecto=10,
        )

        cur.execute.assert_called_once()
        query, params = cur.execute.call_args[0]

        assert 'insert into notificacion' in query.lower()
        assert params['rut_usuario'] == '11111111-1'
        assert params['codigo_tipo'] == TIPO_DESASIGNACION
        assert params['nivel'] == 'INFO'
        assert params['entidad_tipo'] == 'PROSPECTO'
        assert params['entidad_id'] == 10
        assert params['id_prospecto'] == 10
        assert 'Desasignación' in params['titulo']
        assert 'desasignado' in params['mensaje']
        assert 'Cliente Test' in params['mensaje']
        assert params['leible'] is True

    def test_dedupe_key_es_unico_por_evento(self):
        cur = MagicMock()

        registrar_notificacion_desasignacion(
            cur,
            rut_desasignado='11111111-1',
            detalle_asignacion='gestión comercial',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Cliente Test',
            id_prospecto=10,
        )

        _, params = cur.execute.call_args[0]
        assert params['dedupe_key'].startswith(f'{TIPO_DESASIGNACION}:PROSPECTO:10:gestión comercial:')

    def test_no_retorna_nada(self):
        cur = MagicMock()

        resultado = registrar_notificacion_desasignacion(
            cur,
            rut_desasignado='11111111-1',
            detalle_asignacion='asistencia de renovación',
            entidad_tipo='CLIENTE',
            entidad_id=5,
            nombre_entidad='Cliente ABC',
            id_prospecto=3,
        )

        assert resultado is None

    def test_mensaje_incluye_detalle_y_entidad(self):
        cur = MagicMock()

        registrar_notificacion_desasignacion(
            cur,
            rut_desasignado='22222222-2',
            detalle_asignacion='evaluación técnica',
            entidad_tipo='PROSPECTO',
            entidad_id=7,
            nombre_entidad='Empresa XYZ',
            id_prospecto=7,
        )

        _, params = cur.execute.call_args[0]
        assert 'evaluación técnica' in params['mensaje']
        assert 'Empresa XYZ' in params['mensaje']
        assert 'desasignado' in params['mensaje']

    def test_tipo_es_desasignacion_ejecutivo(self):
        cur = MagicMock()

        registrar_notificacion_desasignacion(
            cur,
            rut_desasignado='33333333-3',
            detalle_asignacion='cobranza',
            entidad_tipo='CLIENTE',
            entidad_id=2,
            nombre_entidad='Cliente ABC',
            id_prospecto=1,
        )

        _, params = cur.execute.call_args[0]
        assert params['codigo_tipo'] == 'DESASIGNACION_EJECUTIVO'
