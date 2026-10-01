from unittest.mock import MagicMock

import pytest

from app.infraestructura.notificacion.notificaciones_asignacion import (
    TIPO_ASIGNACION,
    registrar_notificacion_asignacion,
)


@pytest.mark.unit
class TestRegistrarNotificacionAsignacion:

    def test_inserta_notificacion_con_parametros_correctos(self):
        cur = MagicMock()

        registrar_notificacion_asignacion(
            cur,
            rut_asignado='11111111-1',
            rol='ejecutivo comercial',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Cliente Test',
            url_destino='/prospectos?id=10',
        )

        cur.execute.assert_called_once()
        query, params = cur.execute.call_args[0]

        assert 'insert into notificacion' in query.lower()
        assert params['rut_usuario'] == '11111111-1'
        assert params['codigo_tipo'] == TIPO_ASIGNACION
        assert params['nivel'] == 'INFO'
        assert params['entidad_tipo'] == 'PROSPECTO'
        assert params['entidad_id'] == 10
        assert params['url_destino'] == '/prospectos?id=10'
        assert 'ejecutivo comercial' in params['titulo']
        assert 'Cliente Test' in params['mensaje']

    def test_dedupe_key_es_unico_por_evento(self):
        cur = MagicMock()

        registrar_notificacion_asignacion(
            cur,
            rut_asignado='11111111-1',
            rol='ejecutivo comercial',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Cliente Test',
            url_destino='/prospectos?id=10',
        )

        _, params = cur.execute.call_args[0]
        assert params['dedupe_key'].startswith(f'{TIPO_ASIGNACION}:PROSPECTO:10:ejecutivo comercial:')

    def test_no_retorna_nada(self):
        cur = MagicMock()

        resultado = registrar_notificacion_asignacion(
            cur,
            rut_asignado='11111111-1',
            rol='asistente de renovación',
            entidad_tipo='CLIENTE',
            entidad_id=5,
            nombre_entidad='Cliente ABC',
            url_destino='/clientes?id=5',
        )

        assert resultado is None

    def test_mensaje_incluye_rol_y_entidad(self):
        cur = MagicMock()

        registrar_notificacion_asignacion(
            cur,
            rut_asignado='22222222-2',
            rol='asistente de renovación',
            entidad_tipo='CLIENTE',
            entidad_id=5,
            nombre_entidad='Empresa XYZ',
            url_destino='/clientes?id=5',
        )

        _, params = cur.execute.call_args[0]
        assert 'asistente de renovación' in params['mensaje']
        assert 'Empresa XYZ' in params['mensaje']
