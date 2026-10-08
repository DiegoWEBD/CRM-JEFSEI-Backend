from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.dominio.notificacion.repositorio_notificaciones import (
    RepositorioNotificaciones,
)
from tests.factories.notificacion_factory import AHORA_REF, crear_notificacion_mock

AHORA = datetime(2026, 10, 8, 15, 30, 0, tzinfo=timezone.utc)


@pytest.fixture
def repositorio_mock():
    return MagicMock(spec=RepositorioNotificaciones)


@pytest.fixture
def servicio(repositorio_mock):
    return ServicioAlertasProceso(repositorio_mock)


@pytest.mark.unit
class TestServicioAlertasProceso:

    def test_marca_solo_los_tipos_dados(self, servicio, repositorio_mock):
        sla = crear_notificacion_mock(id=1, codigo_tipo='SLA_POR_VENCER')
        fuera_de_tipo = crear_notificacion_mock(id=2, codigo_tipo='FECHA_CIERRE_VENCIDA')
        repositorio_mock.buscar_notificaciones_proceso_comercial.return_value = [
            sla,
            fuera_de_tipo,
        ]

        destinatarios = servicio.marcar_leidas(
            42, ('SLA_POR_VENCER', 'SLA_VENCIDO'), AHORA
        )

        repositorio_mock.buscar_notificaciones_proceso_comercial.assert_called_once_with(42)
        repositorio_mock.actualizar.assert_called_once_with(sla)
        assert sla.leida is True
        assert sla.fecha_leida == AHORA
        assert fuera_de_tipo.leida is False
        assert fuera_de_tipo.fecha_leida is None
        assert destinatarios == ['12345678-9']

    def test_no_remarca_notificaciones_ya_leidas(self, servicio, repositorio_mock):
        leida = crear_notificacion_mock(
            id=1, codigo_tipo='SLA_VENCIDO', leida=True, fecha_leida=AHORA_REF
        )
        repositorio_mock.buscar_notificaciones_proceso_comercial.return_value = [leida]

        destinatarios = servicio.marcar_leidas(
            42, ('SLA_POR_VENCER', 'SLA_VENCIDO'), AHORA
        )

        repositorio_mock.actualizar.assert_not_called()
        assert leida.fecha_leida == AHORA_REF
        assert destinatarios == []

    def test_excluye_alertas_sin_destinatario(self, servicio, repositorio_mock):
        sin_rut = crear_notificacion_mock(id=1, codigo_tipo='SLA_VENCIDO', rut_usuario=None)
        con_rut = crear_notificacion_mock(id=2, codigo_tipo='SLA_POR_VENCER', rut_usuario='99999999-9')
        repositorio_mock.buscar_notificaciones_proceso_comercial.return_value = [sin_rut, con_rut]

        destinatarios = servicio.marcar_leidas(
            42, ('SLA_POR_VENCER', 'SLA_VENCIDO'), AHORA
        )

        assert sin_rut.leida is True
        assert con_rut.leida is True
        assert destinatarios == ['99999999-9']

    def test_sin_notificaciones_devuelve_vacio(self, servicio, repositorio_mock):
        repositorio_mock.buscar_notificaciones_proceso_comercial.return_value = []

        destinatarios = servicio.marcar_leidas(
            42, ('CIERRE_ESTIMADO_PROXIMO', 'FECHA_CIERRE_VENCIDA'), AHORA
        )

        repositorio_mock.actualizar.assert_not_called()
        assert destinatarios == []

    def test_marca_varias_alertas_del_mismo_proceso(self, servicio, repositorio_mock):
        por_vencer = crear_notificacion_mock(id=1, codigo_tipo='SLA_POR_VENCER', rut_usuario='11111111-1')
        vencida = crear_notificacion_mock(id=2, codigo_tipo='SLA_VENCIDO', rut_usuario='22222222-2')
        repositorio_mock.buscar_notificaciones_proceso_comercial.return_value = [por_vencer, vencida]

        destinatarios = servicio.marcar_leidas(
            42, ('SLA_POR_VENCER', 'SLA_VENCIDO'), AHORA
        )

        assert repositorio_mock.actualizar.call_count == 2
        assert por_vencer.fecha_leida == AHORA
        assert vencida.fecha_leida == AHORA
        assert destinatarios == ['11111111-1', '22222222-2']
