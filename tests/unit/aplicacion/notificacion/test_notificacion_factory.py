from datetime import datetime, timezone

import pytest

from app.aplicacion.notificacion.notificacion_factory import NotificacionFactory
from app.dominio.notificacion.tipos_alerta import (
    TIPO_ASIGNACION,
    TIPO_DESASIGNACION,
)

AHORA = datetime(2026, 10, 8, 15, 30, 0, tzinfo=timezone.utc)


@pytest.mark.unit
class TestCrearNotificacionAsignacion:

    def test_campos_de_asignacion(self):
        notificacion = NotificacionFactory.crear_notificacion_asignacion(
            rut_asignado='11111111-1',
            detalle_asignacion='gestión comercial',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Prospecto Test',
            id_prospecto=10,
            ahora=AHORA,
        )

        assert notificacion.id is None
        assert notificacion.rut_usuario == '11111111-1'
        assert notificacion.codigo_tipo == TIPO_ASIGNACION
        assert notificacion.nivel == 'INFO'
        assert notificacion.leible is True
        assert notificacion.leida is False
        assert notificacion.fecha_leida is None
        assert notificacion.created_at == AHORA
        assert notificacion.entidad_tipo == 'PROSPECTO'
        assert notificacion.entidad_id == 10
        assert notificacion.id_prospecto == 10

    def test_titulo_mensaje_y_dedupe_key(self):
        notificacion = NotificacionFactory.crear_notificacion_asignacion(
            rut_asignado='11111111-1',
            detalle_asignacion='gestión comercial',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Prospecto Test',
            id_prospecto=10,
            ahora=AHORA,
        )

        assert notificacion.titulo == 'Asignación de gestión comercial'
        assert notificacion.mensaje == (
            'Se le ha asignado la gestión comercial del prospecto Prospecto Test.'
        )
        assert notificacion.dedupe_key == (
            f'{TIPO_ASIGNACION}:PROSPECTO:10:gestión comercial:{AHORA.isoformat()}'
        )

    def test_entidad_en_minusculas_en_el_mensaje(self):
        notificacion = NotificacionFactory.crear_notificacion_asignacion(
            rut_asignado='11111111-1',
            detalle_asignacion='cobranza',
            entidad_tipo='CLIENTE',
            entidad_id=5,
            nombre_entidad='#5',
            id_prospecto=1,
            ahora=AHORA,
        )

        assert notificacion.mensaje == 'Se le ha asignado la cobranza del cliente #5.'

    def test_permite_rut_nulo(self):
        notificacion = NotificacionFactory.crear_notificacion_asignacion(
            rut_asignado=None,
            detalle_asignacion='gestión comercial',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Prospecto Test',
            id_prospecto=10,
            ahora=AHORA,
        )

        assert notificacion.rut_usuario is None
        assert notificacion.entidad_tipo == 'PROSPECTO'
        assert notificacion.entidad_id == 10
        assert notificacion.id_prospecto == 10
        assert notificacion.mensaje == (
            'Se le ha asignado la gestión comercial del prospecto Prospecto Test.'
        )
        assert notificacion.dedupe_key == (
            f'{TIPO_ASIGNACION}:PROSPECTO:10:gestión comercial:{AHORA.isoformat()}'
        )


@pytest.mark.unit
class TestCrearNotificacionDesasignacion:

    def test_campos_titulo_mensaje_y_dedupe_key(self):
        notificacion = NotificacionFactory.crear_notificacion_desasignacion(
            rut_desasignado='33333333-3',
            detalle_asignacion='evaluación técnica',
            entidad_tipo='PROSPECTO',
            entidad_id=10,
            nombre_entidad='Prospecto Test',
            id_prospecto=10,
            ahora=AHORA,
        )

        assert notificacion.rut_usuario == '33333333-3'
        assert notificacion.codigo_tipo == TIPO_DESASIGNACION
        assert notificacion.nivel == 'INFO'
        assert notificacion.leible is True
        assert notificacion.leida is False
        assert notificacion.titulo == 'Desasignación de evaluación técnica'
        assert notificacion.mensaje == (
            'Se le ha desasignado la evaluación técnica del prospecto Prospecto Test.'
        )
        assert notificacion.dedupe_key == (
            f'{TIPO_DESASIGNACION}:PROSPECTO:10:evaluación técnica:{AHORA.isoformat()}'
        )

    def test_permite_rut_nulo(self):
        notificacion = NotificacionFactory.crear_notificacion_desasignacion(
            rut_desasignado=None,
            detalle_asignacion='cobranza',
            entidad_tipo='CLIENTE',
            entidad_id=5,
            nombre_entidad='Cliente Test',
            id_prospecto=1,
            ahora=AHORA,
        )

        assert notificacion.rut_usuario is None
        assert notificacion.entidad_tipo == 'CLIENTE'
        assert notificacion.entidad_id == 5
        assert notificacion.id_prospecto == 1
        assert notificacion.mensaje == (
            'Se le ha desasignado la cobranza del cliente Cliente Test.'
        )


@pytest.mark.unit
class TestCrearAlertaSla:

    def test_campos_y_dedupe_key_estable(self):
        notificacion = NotificacionFactory.crear_alerta_sla(
            rut_usuario='11111111-1',
            codigo_tipo='SLA_POR_VENCER',
            nivel='AVISO',
            titulo='Oportunidad próximo al límite',
            mensaje='mensaje',
            id_proceso_comercial=42,
            id_prospecto=7,
            codigo_estado='CONTACTO_INICIAL',
            ahora=AHORA,
        )

        assert notificacion.id is None
        assert notificacion.rut_usuario == '11111111-1'
        assert notificacion.codigo_tipo == 'SLA_POR_VENCER'
        assert notificacion.nivel == 'AVISO'
        assert notificacion.titulo == 'Oportunidad próximo al límite'
        assert notificacion.mensaje == 'mensaje'
        assert notificacion.entidad_tipo == 'PROCESO_COMERCIAL'
        assert notificacion.entidad_id == 42
        assert notificacion.id_prospecto == 7
        assert notificacion.leible is False
        assert notificacion.leida is False
        assert notificacion.fecha_leida is None
        assert notificacion.created_at == AHORA
        # Dedupe estable: sin timestamp, el on conflict evita duplicados.
        assert notificacion.dedupe_key == (
            'SLA_POR_VENCER:42:CONTACTO_INICIAL:11111111-1'
        )


@pytest.mark.unit
class TestCrearAlertaCierre:

    def test_campos_y_dedupe_key_con_timestamp(self):
        notificacion = NotificacionFactory.crear_alerta_cierre(
            rut_usuario='11111111-1',
            codigo_tipo='CIERRE_ESTIMADO_PROXIMO',
            nivel='AVISO',
            titulo='Cierre estimado próximo',
            mensaje='mensaje',
            id_proceso_comercial=42,
            id_prospecto=7,
            ahora=AHORA,
        )

        assert notificacion.id is None
        assert notificacion.rut_usuario == '11111111-1'
        assert notificacion.codigo_tipo == 'CIERRE_ESTIMADO_PROXIMO'
        assert notificacion.nivel == 'AVISO'
        assert notificacion.entidad_tipo == 'PROCESO_COMERCIAL'
        assert notificacion.entidad_id == 42
        assert notificacion.id_prospecto == 7
        assert notificacion.leible is False
        assert notificacion.leida is False
        assert notificacion.created_at == AHORA
        assert notificacion.dedupe_key == (
            f'CIERRE_ESTIMADO_PROXIMO:42:11111111-1:{AHORA.isoformat()}'
        )
