from unittest.mock import MagicMock

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import (
    ServicioAlertasProceso,
)
from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import (
    GenerarAlertaRenovacionPolizaUseCase,
)
from app.aplicacion.notificacion.use_cases.reevaluar_alertas_renovacion_descarte import (
    ReevaluarAlertasRenovacionDescarteUseCase,
)
from app.dominio.proceso_comercial.repositorio_procesos_comerciales import (
    RepositorioProcesosComerciales,
)
from tests.factories.notificacion_factory import AHORA_REF, crear_notificacion_mock


def _alerta(codigo_tipo, rut='11111111-1'):
    return crear_notificacion_mock(
        id=None,
        codigo_tipo=codigo_tipo,
        rut_usuario=rut,
        numero_poliza='POL-001',
    )


def _use_case(*, numero_poliza_base='POL-001', eliminar=None, creadas=None,
              marcados=None):
    repo_procesos = MagicMock(spec=RepositorioProcesosComerciales)
    repo_procesos.obtener_poliza_base_renovacion.return_value = numero_poliza_base

    servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
    servicio_alertas.eliminar_renovacion.return_value = eliminar or []
    servicio_alertas.marcar_leidas_renovacion.return_value = marcados or []

    generar = MagicMock(spec=GenerarAlertaRenovacionPolizaUseCase)
    generar.ejecutar.return_value = creadas or []

    return (
        ReevaluarAlertasRenovacionDescarteUseCase(
            repo_procesos, servicio_alertas, generar
        ),
        repo_procesos,
        servicio_alertas,
        generar,
    )


@pytest.mark.unit
class TestReevaluarAlertasRenovacionDescarte:

    def test_proceso_sin_poliza_base_no_hace_nada(self):
        uc, repo_procesos, servicio_alertas, generar = _use_case(
            numero_poliza_base=None
        )

        assert uc.ejecutar(7, AHORA_REF) == []
        servicio_alertas.eliminar_renovacion.assert_not_called()
        generar.ejecutar.assert_not_called()

    def test_consulta_la_poliza_base_del_proceso(self):
        uc, repo_procesos, servicio_alertas, generar = _use_case()

        uc.ejecutar(7, AHORA_REF)

        repo_procesos.obtener_poliza_base_renovacion.assert_called_once_with(7)

    def test_elimina_alertas_antiguas_antes_de_recrear(self):
        orden = []
        uc, repo_procesos, servicio_alertas, generar = _use_case()

        def _eliminar(numero_poliza):
            orden.append('eliminar')
            return []

        def _recrear(numero_poliza, ahora):
            orden.append('recrear')
            return []

        servicio_alertas.eliminar_renovacion.side_effect = _eliminar
        generar.ejecutar.side_effect = _recrear

        uc.ejecutar(7, AHORA_REF)

        assert orden == ['eliminar', 'recrear']

    def test_elimina_y_regenera_sobre_la_poliza_base(self):
        uc, repo_procesos, servicio_alertas, generar = _use_case()

        uc.ejecutar(7, AHORA_REF)

        servicio_alertas.eliminar_renovacion.assert_called_once_with('POL-001')
        generar.ejecutar.assert_called_once_with('POL-001', AHORA_REF)

    def test_devuelve_los_destinatarios_afectados_sin_repetidos(self):
        uc, repo_procesos, servicio_alertas, generar = _use_case(
            eliminar=['11111111-1'],
            creadas=[
                _alerta('RENOVACION_POLIZA_VENCIDA', rut='11111111-1'),
                _alerta('RENOVACION_POLIZA_VENCIDA', rut='22222222-2'),
            ],
            marcados=['11111111-1'],
        )

        assert uc.ejecutar(7, AHORA_REF) == ['11111111-1', '22222222-2']

    def test_vencida_resuelve_cotizacion_y_gestion(self):
        uc, repo_procesos, servicio_alertas, generar = _use_case(
            creadas=[
                _alerta('RENOVACION_COTIZACION_PENDIENTE'),
                _alerta('RENOVACION_GESTION_PENDIENTE'),
                _alerta('RENOVACION_POLIZA_VENCIDA'),
            ],
        )

        uc.ejecutar(7, AHORA_REF)

        servicio_alertas.marcar_leidas_renovacion.assert_called_once_with(
            'POL-001',
            AHORA_REF,
            tipos=(
                'RENOVACION_COTIZACION_PENDIENTE',
                'RENOVACION_GESTION_PENDIENTE',
            ),
        )

    def test_gestion_resuelve_solo_la_cotizacion(self):
        uc, repo_procesos, servicio_alertas, generar = _use_case(
            creadas=[
                _alerta('RENOVACION_COTIZACION_PENDIENTE'),
                _alerta('RENOVACION_GESTION_PENDIENTE'),
            ],
        )

        uc.ejecutar(7, AHORA_REF)

        servicio_alertas.marcar_leidas_renovacion.assert_called_once_with(
            'POL-001',
            AHORA_REF,
            tipos=('RENOVACION_COTIZACION_PENDIENTE',),
        )

    def test_solo_cotizacion_no_resuelve_nada(self):
        uc, repo_procesos, servicio_alertas, generar = _use_case(
            creadas=[_alerta('RENOVACION_COTIZACION_PENDIENTE')],
        )

        uc.ejecutar(7, AHORA_REF)

        servicio_alertas.marcar_leidas_renovacion.assert_not_called()

    def test_sin_alertas_creadas_no_resuelve_nada(self):
        uc, repo_procesos, servicio_alertas, generar = _use_case()

        uc.ejecutar(7, AHORA_REF)

        servicio_alertas.marcar_leidas_renovacion.assert_not_called()
