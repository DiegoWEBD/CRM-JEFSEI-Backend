from unittest.mock import MagicMock, patch

import pytest

from app.aplicacion.notificacion.servicios.servicio_alertas_proceso import ServicioAlertasProceso
from app.aplicacion.notificacion.use_cases.generar_alerta_renovacion_poliza import (
    GenerarAlertaRenovacionPolizaUseCase,
)
from app.aplicacion.notificacion.use_cases.generar_alertas_renovacion import (
    GenerarAlertasRenovacionUseCase,
)
from app.core.hub_notificaciones import EVENTO_NOTIFICACIONES_ACTUALIZADAS
from app.dominio.notificacion.repositorio_notificaciones import RepositorioNotificaciones
from tests.factories.notificacion_factory import (
    AHORA_REF,
    crear_notificacion_mock,
    crear_poliza_alertable_renovacion_mock,
)

MODULO = 'app.aplicacion.notificacion.use_cases.generar_alertas_renovacion'


def _use_case(polizas, *, servicio_alertas=None):
    repo = MagicMock(spec=RepositorioNotificaciones)
    repo.obtener_polizas_alertables_renovacion.return_value = polizas
    repo.registrar.return_value = True
    generar = MagicMock(spec=GenerarAlertaRenovacionPolizaUseCase)
    if servicio_alertas is None:
        servicio_alertas = MagicMock(spec=ServicioAlertasProceso)
        servicio_alertas.marcar_leidas_renovacion.return_value = []
    return (
        GenerarAlertasRenovacionUseCase(repo, generar, servicio_alertas),
        repo,
        generar,
    )


@pytest.mark.unit
class TestGenerarAlertasRenovacion:

    @patch(f'{MODULO}.hub')
    def test_registra_las_alertas_de_cada_poliza(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alerta = crear_notificacion_mock(
            id=None, codigo_tipo='RENOVACION_GESTION_PENDIENTE', rut_usuario='11111111-1'
        )
        uc, repo, generar = _use_case([poliza])
        generar.evaluar.return_value = [alerta]

        creadas = uc.ejecutar(AHORA_REF)

        generar.evaluar.assert_called_once_with(poliza, AHORA_REF)
        repo.registrar.assert_called_once_with(alerta)
        assert creadas == [alerta]
        hub_mock.publicar_desde_hilo.assert_called_once()

    @patch(f'{MODULO}.hub')
    def test_no_duplica_alertas_ya_registradas(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alerta = crear_notificacion_mock(
            id=None, codigo_tipo='RENOVACION_GESTION_PENDIENTE', rut_usuario='11111111-1'
        )
        uc, repo, generar = _use_case([poliza])
        generar.evaluar.return_value = [alerta]
        repo.registrar.return_value = False

        creadas = uc.ejecutar(AHORA_REF)

        assert creadas == []
        hub_mock.publicar_desde_hilo.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_sin_alertas_no_publica(self, hub_mock):
        uc, repo, generar = _use_case([crear_poliza_alertable_renovacion_mock()])
        generar.evaluar.return_value = []

        assert uc.ejecutar(AHORA_REF) == []
        repo.registrar.assert_not_called()
        hub_mock.publicar_desde_hilo.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_publica_los_destinatarios_de_las_alertas_creadas(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        alertas = [
            crear_notificacion_mock(
                id=None,
                codigo_tipo='RENOVACION_COTIZACION_PENDIENTE',
                rut_usuario='11111111-1',
            ),
            crear_notificacion_mock(
                id=None,
                codigo_tipo='RENOVACION_COTIZACION_PENDIENTE',
                rut_usuario='22222222-2',
            ),
        ]
        uc, repo, generar = _use_case([poliza])
        generar.evaluar.return_value = alertas

        uc.ejecutar(AHORA_REF)

        destinatarios = list(hub_mock.publicar_desde_hilo.call_args.args[0])
        assert sorted(destinatarios) == ['11111111-1', '22222222-2']

    @patch(f'{MODULO}.hub')
    def test_evalua_todas_las_polizas_alertables(self, hub_mock):
        polizas = [
            crear_poliza_alertable_renovacion_mock(numero_poliza=f'POL-00{i}')
            for i in range(3)
        ]
        uc, repo, generar = _use_case(polizas)
        generar.evaluar.return_value = []

        uc.ejecutar(AHORA_REF)

        assert generar.evaluar.call_count == 3


@pytest.mark.unit
class TestResolverEscalonesDeAlertasRenovacion:

    def _servicio(self, marcados=None):
        servicio = MagicMock(spec=ServicioAlertasProceso)
        servicio.marcar_leidas_renovacion.return_value = marcados or []
        return servicio

    def _alerta(self, codigo_tipo, rut='11111111-1'):
        return crear_notificacion_mock(id=None, codigo_tipo=codigo_tipo, rut_usuario=rut)

    @patch(f'{MODULO}.hub')
    def test_vencida_resuelve_cotizacion_y_gestion(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        servicio = self._servicio()
        uc, repo, generar = _use_case([poliza], servicio_alertas=servicio)
        generar.evaluar.return_value = [
            self._alerta('RENOVACION_COTIZACION_PENDIENTE'),
            self._alerta('RENOVACION_GESTION_PENDIENTE'),
            self._alerta('RENOVACION_POLIZA_VENCIDA'),
        ]

        uc.ejecutar(AHORA_REF)

        servicio.marcar_leidas_renovacion.assert_called_once_with(
            'POL-001',
            AHORA_REF,
            tipos=(
                'RENOVACION_COTIZACION_PENDIENTE',
                'RENOVACION_GESTION_PENDIENTE',
            ),
        )

    @patch(f'{MODULO}.hub')
    def test_gestion_resuelve_solo_la_cotizacion(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        servicio = self._servicio()
        uc, repo, generar = _use_case([poliza], servicio_alertas=servicio)
        generar.evaluar.return_value = [
            self._alerta('RENOVACION_COTIZACION_PENDIENTE'),
            self._alerta('RENOVACION_GESTION_PENDIENTE'),
        ]

        uc.ejecutar(AHORA_REF)

        servicio.marcar_leidas_renovacion.assert_called_once_with(
            'POL-001',
            AHORA_REF,
            tipos=('RENOVACION_COTIZACION_PENDIENTE',),
        )

    @patch(f'{MODULO}.hub')
    def test_solo_cotizacion_no_resuelve_nada(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        servicio = self._servicio()
        uc, repo, generar = _use_case([poliza], servicio_alertas=servicio)
        generar.evaluar.return_value = [self._alerta('RENOVACION_COTIZACION_PENDIENTE')]

        uc.ejecutar(AHORA_REF)

        servicio.marcar_leidas_renovacion.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_sin_alertas_no_resuelve_nada(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        servicio = self._servicio()
        uc, repo, generar = _use_case([poliza], servicio_alertas=servicio)
        generar.evaluar.return_value = []

        uc.ejecutar(AHORA_REF)

        servicio.marcar_leidas_renovacion.assert_not_called()

    @patch(f'{MODULO}.hub')
    def test_publica_los_destinatarios_de_las_alertas_resueltas(self, hub_mock):
        poliza = crear_poliza_alertable_renovacion_mock()
        servicio = self._servicio(marcados=['11111111-1', '22222222-2'])
        uc, repo, generar = _use_case([poliza], servicio_alertas=servicio)
        generar.evaluar.return_value = [self._alerta('RENOVACION_POLIZA_VENCIDA')]
        repo.registrar.return_value = False

        uc.ejecutar(AHORA_REF)

        hub_mock.publicar_desde_hilo.assert_called_once_with(
            ['11111111-1', '22222222-2'],
            {
                'evento': EVENTO_NOTIFICACIONES_ACTUALIZADAS,
                'motivo': 'alertas_renovacion_resueltas',
            },
        )
