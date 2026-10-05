from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.infraestructura.notificacion.alertas_por_proceso import (
    TIPOS_ALERTA_SLA,
    marcar_alertas_sla_leidas,
    reasignar_destinatario_alertas,
)


def _cursor_con_fetchall(rows, rowcount: int = 0) -> MagicMock:
    cur = MagicMock()
    cur.fetchall.return_value = rows
    cur.rowcount = rowcount
    return cur


@pytest.mark.unit
class TestMarcarAlertasSlaLeidas:

    def test_ejecuta_update_sobre_alertas_no_leidas_del_proceso(self):
        cur = _cursor_con_fetchall([{'rut_usuario': '11111111-1'}])
        fecha = datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)

        ruts = marcar_alertas_sla_leidas(cur, id_proceso=7, fecha=fecha)

        query = cur.execute.call_args.args[0].lower()
        params = cur.execute.call_args.args[1]

        assert 'update notificacion' in query
        assert 'leida = false' in query
        assert "entidad_tipo = 'proceso_comercial'" in query
        assert 'entidad_id = %(id_proceso)s' in query
        assert 'codigo_tipo = any(%(tipos_sla)s)' in query
        assert 'fecha_leida = %(fecha)s' in query
        assert params == {
            'fecha': fecha,
            'id_proceso': 7,
            'tipos_sla': list(TIPOS_ALERTA_SLA),
        }
        assert ruts == ['11111111-1']

    def test_solo_tipos_sla(self):
        assert TIPOS_ALERTA_SLA == ('SLA_POR_VENCER', 'SLA_VENCIDO')

    def test_sin_alertas_devuelve_vacio(self):
        cur = _cursor_con_fetchall([])
        fecha = datetime.now(tz=timezone.utc)

        assert marcar_alertas_sla_leidas(cur, id_proceso=1, fecha=fecha) == []

    def test_descarta_destinatarios_null(self):
        cur = _cursor_con_fetchall([
            {'rut_usuario': '11111111-1'},
            {'rut_usuario': None},
        ])
        fecha = datetime.now(tz=timezone.utc)

        ruts = marcar_alertas_sla_leidas(cur, id_proceso=1, fecha=fecha)

        assert ruts == ['11111111-1']


@pytest.mark.unit
class TestReasignarDestinatarioAlertas:

    def _condiciones_en(self, cur) -> str:
        # Las queries van compuestas con psycopg.sql: str() da el repr,
        # para obtener el SQL hay que usar as_string().
        consultas = ' '.join(
            call.args[0].as_string(None).lower()
            for call in cur.execute.call_args_list
        )
        return consultas

    def test_filtra_por_rol_del_estado_siguiente_y_procesos_abiertos(self):
        cur = _cursor_con_fetchall([{'rut_usuario': '11111111-1'}], rowcount=1)

        reasignar_destinatario_alertas(
            cur, id_prospecto=3, rol='EJECUTIVO_COMERCIAL', nuevo_rut='22222222-2'
        )

        consultas = self._condiciones_en(cur)
        assert 'update notificacion' in consultas
        assert 'ei_siguiente.rol_responsable = %(rol)s' in consultas
        assert 'pc.codigo_estado_actual' in consultas
        assert 'pc.cerrado = false' in consultas
        assert 'n.leida = false' in consultas
        assert 'n.rut_usuario is distinct from %(nuevo_rut)s' in consultas
        assert 'transicionestadoprocesocomercial' in consultas
        assert 'es_principal' in consultas

        assert cur.execute.call_count == 2
        for call in cur.execute.call_args_list:
            params = call.args[1]
            assert params['id_prospecto'] == 3
            assert params['rol'] == 'EJECUTIVO_COMERCIAL'
            assert params['nuevo_rut'] == '22222222-2'

    def test_devuelve_previos_y_nuevos(self):
        cur = _cursor_con_fetchall(
            [{'rut_usuario': '11111111-1'}, {'rut_usuario': '11111111-1'}],
            rowcount=1,
        )

        previos, nuevos = reasignar_destinatario_alertas(
            cur, id_prospecto=3, rol='EJECUTIVO_COMERCIAL', nuevo_rut='22222222-2'
        )

        assert previos == {'11111111-1'}
        assert nuevos == {'22222222-2'}

    def test_desasignacion_pone_destinatario_null_y_solo_notifica_previos(self):
        cur = _cursor_con_fetchall([{'rut_usuario': '11111111-1'}], rowcount=1)

        previos, nuevos = reasignar_destinatario_alertas(
            cur, id_prospecto=3, rol='EJECUTIVO_COMERCIAL', nuevo_rut=None
        )

        params = cur.execute.call_args_list[1].args[1]
        assert params['nuevo_rut'] is None
        assert previos == {'11111111-1'}
        assert nuevos == set()

    def test_sin_filas_afectadas_devuelve_vacio(self):
        cur = _cursor_con_fetchall([{'rut_usuario': '11111111-1'}], rowcount=0)

        previos, nuevos = reasignar_destinatario_alertas(
            cur, id_prospecto=3, rol='EJECUTIVO_COMERCIAL', nuevo_rut='22222222-2'
        )

        assert previos == set()
        assert nuevos == set()

    def test_reclama_alertas_huerfanas_sin_notificar_a_null(self):
        # Alertas huérfanas (rut_usuario NULL) no generan destinatario previo,
        # pero igual deben ser reclamadas por el nuevo ejecutivo.
        cur = _cursor_con_fetchall([{'rut_usuario': None}], rowcount=1)

        previos, nuevos = reasignar_destinatario_alertas(
            cur, id_prospecto=3, rol='EJECUTIVO_EVALUACION_PROYECTOS', nuevo_rut='33333333-3'
        )

        assert previos == set()
        assert nuevos == {'33333333-3'}
